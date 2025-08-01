"""Command-line interface entrypoint for the `foldifyai` package."""
from __future__ import annotations
import time 
from colorama import Fore, Style

import base64
import zipfile
import io
import pathlib
import sys
from pathlib import Path
from tqdm import tqdm
import os 
import time 
import json 
from rdkit import Chem
from rdkit.Chem import AllChem
import urllib
from foldifyai.utils import get_type
import requests
try: 
    from logmd import LogMD
except:
    pass 


def _usage() -> None:
    """Print a short help message using the actual executable name."""
    prog = pathlib.Path(sys.argv[0]).name or "foldify"
    print(f"Usage: {prog} <path_to_file.fasta>", file=sys.stderr)


def compute_3d_conformer(mol, version: str = "v3") -> bool:
    if version == "v3":
        options = AllChem.ETKDGv3()
    elif version == "v2":
        options = AllChem.ETKDGv2()
    else:
        options = AllChem.ETKDGv2()

    options.clearConfs = False
    conf_id = -1

    options.timeout = 3 # don't spend more than three seconds on AllChem.EmbedMolecule
    #options.maxIterations = 10 # don't spend more than 10 attempts (default is 100?)

    try:
        conf_id = AllChem.EmbedMolecule(mol, options)#, maxAttempts=0)

        if conf_id == -1:
            print(
                f"WARNING: RDKit ETKDGv3 failed to generate a conformer for molecule "
                f"{Chem.MolToSmiles(AllChem.RemoveHs(mol))}, so the program will start with random coordinates. "
                f"Note that the performance of the model under this behaviour was not tested."
            )
            options.useRandomCoords = True
            return False # conf_id = AllChem.EmbedMolecule(mol, options)

        #AllChem.UFFOptimizeMolecule(mol, confId=conf_id, maxIters=1000)
        # i set the maxIters=33 to skip more aggressively.
        AllChem.UFFOptimizeMolecule(mol, confId=conf_id, maxIters=33)

    except RuntimeError:
        return False 
        pass  # Force field issue here
    except ValueError:
        return False 
        pass  # sanitization issue here

    if conf_id != -1:
        conformer = mol.GetConformer(conf_id)
        conformer.SetProp("name", "Computed")
        conformer.SetProp("coord_generation", f"ETKDG{version}")
        return True

    return False

def test(seq, affinity=False):
    try:
        mol = AllChem.MolFromSmiles(seq)
        mol = AllChem.AddHs(mol)

        # Set atom names
        canonical_order = AllChem.CanonicalRankAtoms(mol)
        for atom, can_idx in zip(mol.GetAtoms(), canonical_order):
            atom_name = atom.GetSymbol().upper() + str(can_idx + 1)
            if len(atom_name) > 4:
                msg = (
                    f"{seq} has an atom with a name longer than "
                    f"4 characters: {atom_name}."
                )
                raise ValueError(msg)
                return False 
            atom.SetProp("name", atom_name)

        success = compute_3d_conformer(mol)
        if not success:
            msg = f"Failed to compute 3D conformer for {seq}"
            return False 
            raise ValueError(msg)

        mol_no_h = AllChem.RemoveHs(mol, sanitize=False)
        affinity_mw = AllChem.Descriptors.MolWt(mol_no_h) if affinity else None
        return True
    except Exception as e:
        print(e, seq)
        return False 

def fold(args):
    folder = args.input
    log = args.logmd 
    if args.input.endswith('.fasta'):
        files = [args.input]
        folder = folder.replace('.fasta', '')
    else:
        files = [a for a in Path(folder).rglob("*.fasta")]
        files = sorted(files, key=lambda p: os.path.getsize(str(p)))
        files = [str(a) for a in files]

    if log: 
        l = LogMD()

    output_dir = f"foldify_{folder}/"

    pbar = tqdm(files[::-1])
    for c,p in enumerate(pbar):

        path = f"{output_dir}/{p.replace('.fasta', '')}/"
        if os.path.exists(f"{path}boltz2_prediction.pdb"):
            print(f"Skipping {p} found {path}boltz2_prediction.pdb")
            continue 


        try: 
            t0 = time.time()
            skip = False 
            p = str(p)

            # change this to point to output_dir
            #new_path = p.replace('.fasta','_raw.pdb')
            #if os.path.exists(new_path): continue 

            content = open(p).read()
            num_tokens = sum([len(line) for line in content.split('\n') if not line.startswith('>')])
            #print(num_tokens)
            #if num_tokens > 1000: continue 

            if False:  # this killed my desktop
                for line in content.split('\n'):
                    if line.startswith('>'): continue 
                    if line == '': continue 
                    if get_type(line) == 'SMILES': 
                        if not test(line): 
                            print(f"Skipping {p}. RDKit didn't like {line}. ")
                            #open(new_path, 'w').write(f"Skipping {p}. RDKit didn't like {line}. ")
                            skip = True 
                        else: print('ok')
                if skip: continue 
            encoded = urllib.parse.quote(content, safe="")
            if len(content) == 0: 
                continue 

            url = f"{args.host}/fold?only_return_zip=True&seq={encoded}&{args.args}"

            # Open connection with progress reporting
            response = urllib.request.urlopen(url)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            #progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, 
            #                    desc=f"Foldify")
            
            result = ''
            while True:
                data = response.read(block_size)
                if not data:
                    break
                result += data.decode('utf-8')
                #pbar.update(len(data))
                pbar.set_description(f"{Fore.BLUE}{Style.BRIGHT}[Foldify]{Style.RESET_ALL} {time.strftime('%d-%m %H:%M:%S')} {p} tokens={num_tokens} {len(result)/1000}KB")
                #print(f"[Foldify]{Style.RESET_ALL} {p} -  {num_tokens} - {len(result)/1000}KB")

            #pbar.close()

            #with open(new_path, 'w') as f: f.write(result)
            jsons = [json.loads(a) for a in result.split('\n@\n') if a != '']
            # last is a zip file, unzip. 
            b64_zip_data = jsons[-1]['data']

            zip_bytes = base64.b64decode(b64_zip_data)
            zip_in_memory = io.BytesIO(zip_bytes)
            with zipfile.ZipFile(zip_in_memory, 'r') as zip_ref:
                os.makedirs(path, exist_ok=True)
                zip_ref.extractall(path)

            time.sleep(1)

        except Exception as e: 
            print('something wrong', e)
            print(url)
            pass 
        time.sleep(1)
        print('')
        #exit()


def main() -> None:  # pragma: no cover

    import argparse

    parser = argparse.ArgumentParser(description='Foldify.ai CLI', add_help=False)
    parser.add_argument('-input', '-i', type=str, help='')
    parser.add_argument('-args', type=str, help='')
    parser.add_argument('-logmd', action='store_true', help='Log with LogMD')
    parser.add_argument('-host', '-h', type=str, default='https://gpu1.foldify.org', help='Host URL for Foldify API')
    parser.add_argument('-y', action='store_true', help='Pre-accept using remote host. ')
    args = parser.parse_args()

    if args.host == 'https://gpu1.foldify.org' and not args.y:
        print("You didn't specify host. The default is a remote. ")
        print("Reply `REMOTE` if you want to send sequences. ")
        if input() != 'REMOTE': 
            print('Exiting.')
            exit()
        else: 
            print("Using remote host. ")
            print("You can skip this check with `foldify -y`")


    fold(args)


if __name__ == "__main__":  # pragma: no cover
    sys.argv = ['foldifyai','cofactors/']
    main() 
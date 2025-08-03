import os
import sys
import pandas as pd
import re
import logging
from pathlib import Path
from Bio.PDB import PDBParser, PDBIO, Select


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)


def clean_plt(ax):
    '''Define plotting aesthetics'''
    ax.tick_params(direction='out', length=2, width=1.0)
    ax.spines['bottom'].set_linewidth(1.0)
    ax.spines['top'].set_linewidth(0)
    ax.spines['left'].set_linewidth(1.0)
    ax.spines['right'].set_linewidth(0)
    ax.tick_params(labelsize=10.0)
    ax.tick_params(axis='x', which='major', pad=2.0)
    ax.tick_params(axis='y', which='major', pad=2.0)
    return ax

def log_section(title: str):
    '''Define logging title aestethics'''
    border = "#" * 60
    logger.info(f"\n{border}")
    logger.info(f"### {title.upper().center(52)} ###")
    logger.info(f"{border}\n")

def log_subsection(title: str):
    '''Define logging subtitle aestethics'''
    border = "#" * 60
    logger.info(f"\n{border}")
    logger.info(f"### {title.center(52)} ###")
    logger.info(f"{border}\n")

def log_boxed_note(text):
    '''Define logging note aestethics'''
    border = "-" * (len(text) + 8)
    print(f"\n{border}\n|   {text}   |\n{border}\n")

def generate_boltz_structure_path(input_path):
    """
    Generate the structure file path of Boltz structure based on boltz output directory.
    """
    base_path = Path(input_path)
    base_name = base_path.name  
    new_path = base_path / f"boltz_results_{base_name}" / "predictions" / base_name / f"{base_name}_model_0.cif"
    print(new_path)
    return new_path



def clean_protein_sequence(seq: str) -> str:
    """
    Cleans a protein sequence by:
    - Removing stop codons (*)
    - Removing whitespace or newline characters
    - Ensuring only valid amino acid letters remain (A-Z except B, J, O, U, X, Z)
    """
    if pd.isna(seq):
        return None
    seq = seq.upper()
    seq = re.sub(r'[^ACDEFGHIKLMNPQRSTVWY]', '', seq)  # Keep only standard 20 amino acids
    return seq


def delete_empty_subdirs(directory):
    '''Delete empty subdirectories'''
    directory = Path(directory)
    for subdir in directory.iterdir():
        if subdir.is_dir() and not any(subdir.iterdir()):
            subdir.rmdir()
            print(f"Deleted empty directory: {subdir}")

class LigandSelect(Select):
    def __init__(self, ligand_resname):
        self.ligand_resname = ligand_resname

    def accept_residue(self, residue):
        return residue.get_resname() == self.ligand_resname

def extract_ligand_from_PDB(input_pdb, output_pdb, ligand_resname):
    """
    Extracts a ligand from a PDB file and writes it to a new PDB.

    Parameters:
    - input_pdb: str, path to the complex PDB file
    - output_pdb: str, path to write the ligand-only PDB file
    - ligand_resname: str, 3-letter residue name of the ligand (e.g., 'LIG')
    """
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("docked", input_pdb)

    io = PDBIO()
    io.set_structure(structure)
    io.save(str(output_pdb), LigandSelect(ligand_resname))
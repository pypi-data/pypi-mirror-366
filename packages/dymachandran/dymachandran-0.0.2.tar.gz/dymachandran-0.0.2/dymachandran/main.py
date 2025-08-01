#importando as bibliotecas necessarias
import MDAnalysis as mda
from MDAnalysis.analysis.dihedrals import Dihedral, calc_dihedrals
import numpy as np
import pandas as pd
import plotly.express as px
from multiprocessing import Pool
import argparse
import os
from PIL import Image
import requests
from io import BytesIO
import progressbar #instale o progressbar2
#criando uma classe para o gráfico de Ramachandran
class RamachandranPlot:

    def __init__(self, topology_path, trajectory_path, num_processes, output_file): 
        self.topology_path = topology_path #armazena a topologia da estrutura
        self.trajectory_path = trajectory_path #armazena a trajetoria da estrutura
        self.universe = mda.Universe(topology_path, trajectory_path) #armazena o sistema com topologia e trajetoria
        self.protein = self.universe.select_atoms('protein') #armazena a estrutura apenas da proteina
        self.num_processes = num_processes #armazena o numero de processos que vao ser utilizados para rodar o programa
        self.output_file = output_file
    
    def calcular_diedro(self, a,b,c,d):
        # Calcula o ângulo diedro entre quatro átomos
        return mda.lib.mdamath.dihedral(b-a, c-b, d-c)

    def calcular_angulos_phi_psi(self, ts_range):
        phis = []
        psis = []
        frames = []
        residues = []
        resnames = []

        protein = self.protein  # Selecione os átomos da proteína uma vez
        n_atoms = protein.select_atoms('name N')
        ca_atoms = protein.select_atoms('name CA')
        c_atoms = protein.select_atoms('name C')

        # Inicializa a barra de progresso
        total_calculations = (ts_range[1] - ts_range[0]) * (len(ca_atoms) - 2)
        bar = progressbar.ProgressBar(maxval=total_calculations).start()

        progress = 0
        for ts in self.universe.trajectory[ts_range[0]:ts_range[1]]:
            frame_residues = [residue.resname for residue in protein.residues]
            
            for i in range(1, len(ca_atoms) - 1):
                # Calcula os ângulos phi e psi
                phi = -np.degrees(self.calcular_diedro(
                    c_atoms.positions[i-1],  # C(i-1)
                    n_atoms.positions[i],    # N(i)
                    ca_atoms.positions[i],   # CA(i)
                    c_atoms.positions[i]     # C(i)
                ))
                psi = -np.degrees(self.calcular_diedro(
                    n_atoms.positions[i],    # N(i)
                    ca_atoms.positions[i],   # CA(i)
                    c_atoms.positions[i],    # C(i)
                    n_atoms.positions[i+1]   # N(i+1)
                ))

                # Armazena os ângulos e informações adicionais
                phis.append(phi)
                psis.append(psi)
                frames.append(ts.frame+1)
                residues.append(i+1)
                resnames.append(frame_residues[i])

                progress += 1
                bar.update(progress)

        bar.finish()
        return phis, psis, frames, residues, resnames
    def criar_grafico(self): #funcao que cria o grafico propriamente dito
        ts_ranges = [(i * len(self.universe.trajectory) // self.num_processes, (i + 1) * len(self.universe.trajectory) // self.num_processes) for i in range(self.num_processes)]
        
        with Pool(self.num_processes) as pool: #utiliza o numero de processadores 
            results = pool.map(self.calcular_angulos_phi_psi, ts_ranges)
        
        phis, psis, frames, residues, resnames = zip(*results)
        
        # transforma uma lista de listas em uma lista unica
        phis = [phi for sublist in phis for phi in sublist]
        psis = [psi for sublist in psis for psi in sublist]
        frames = [frame for sublist in frames for frame in sublist]
        residues = [residue for sublist in residues for residue in sublist]
        resnames = [resname for sublist in resnames for resname in sublist]

        # cria o DataFrame para ser usado no grafico movel e interativo
        df = pd.DataFrame({
            "phi": phis,
            "psi": psis,
            "frame": frames,
            "residue": residues,
            "resnames": resnames 
        })

        # cria o grafico de Ramachandran interativo
        fig = px.scatter(df, x="phi", y="psi", animation_frame="frame", animation_group="residue", hover_data=["residue", "resnames"],
                        title="Gráfico de Ramachandran por Frame", width= 600, height= 700)
        imagem_url = requests.get('https://github.com/monteirotorres/images/blob/master/bg.png?raw=true') #pega a imagem de fundo de um link
        background = Image.open(BytesIO(imagem_url.content))

        # adiciona a imagem de fundo
        fig.update_layout(
                    images= [dict(
                    source=background,
                    xref="paper", yref="paper",
                    x=0, y=1,
                    sizex=1, sizey=1,
                    xanchor="left",
                    yanchor="top",
                    sizing="stretch",
                    layer="below")]
        )
        
        # ajustando o layout do gráfico
        fig.update_layout(
                    xaxis_title="Phi (°)",
                    yaxis_title="Psi (°)",
                    xaxis=dict(range=[-180, 180]),
                    yaxis=dict(range=[-180, 180]),
                    showlegend=False,
                    plot_bgcolor='rgb(230,230,250)',  
                    paper_bgcolor='rgb(245,255,250)'  
        )

        # adiciona títulos e rótulos
        fig.update_layout(
                    title_text="Gráfico de Ramachandran Interativo",
                    xaxis_title="Ângulo Phi (°)",
                    yaxis_title="Ângulo Psi (°)",
                    font=dict(
                    family="Arial, sans-serif",
                    size=15,
                    color="black"),
                    legend=dict(
                    title="Resíduo",
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1)
        )

        # adiciona marcadores e ajusta a opacidade
        fig.update_traces(marker=dict(size=7, opacity=1, line=dict(width=1)))

        # salva o grafico
        fig.write_html(self.output_file)
        print(" Seu arquivo foi escrito com sucesso\nObrigado por usar o dymachandran")
        

def main(): #chama a funcao principal na linha de comando com argparse
    parser = argparse.ArgumentParser(description='Plote gráficos de Ramachandran a partir de seus arquivos de topologia e trajetória. Certifique-se de instalar as bibliotecas necessarias', epilog='Obrigado por usar o dymachandran',
                                     usage='modo de uso: dymachandran.py [-h] "topology_file.gro" "trajectory_file.xtc" "num_processes" "output_file.html"')
    parser.add_argument('topology', type=str,help='Caminho para o arquivo de topologia .gro')
    parser.add_argument('trajectory', type=str, help='Caminho para o arquivo de trajetória .xtc')
    parser.add_argument('num_processes', type=int, help="Numero de processos usados para rodar o programa")
    parser.add_argument('output_file', type=str, help="Nome do arquivo de saída .html")
    args = parser.parse_args()

    # verifica se os arquivos existem
    if not os.path.isfile(args.topology):
        print(f"Erro: O arquivo de topologia '{args.topology}' não existe ou não está no diretório correto.")
        print(parser.usage)
        return
    if not os.path.isfile(args.trajectory):
        print(f"Erro: O arquivo de trajetória '{args.trajectory}' não existe ou não está no diretório correto.")
        print(parser.usage)
        return

    # verifica a extensao dos arquivos 
    valid_topology_extensions = ['.gro']
    valid_trajectory_extensions = ['.xtc']
    valid_output_file_extensions = ['.html']
    if not any(args.topology.endswith(ext) for ext in valid_topology_extensions):
        print(f"Erro: O arquivo de topologia '{args.topology}' não está em um formato válido.")
        print(parser.usage)
        return

    if not any(args.trajectory.endswith(ext) for ext in valid_trajectory_extensions):
        print(f"Erro: O arquivo de trajetória '{args.trajectory}' não está em um formato válido.")
        print(parser.usage)
        return
    
    if not any(args.output_file.endswith(ext) for ext in valid_output_file_extensions):
        print('O arquivo de saída deve ser .html')
        print(parser.usage)
        return

    try:
        # cria uma instancia da classe RamachandranPlot
        ramachandran_plot = RamachandranPlot(args.topology, args.trajectory, args.num_processes, args.output_file)

        # cria e mostra o gráfico
        ramachandran_plot.criar_grafico()
    except Exception as e:
        print(f"Ocorreu um erro ao gerar o gráfico de Ramachandran: {e}")
    

if __name__ == "__main__":
    main()

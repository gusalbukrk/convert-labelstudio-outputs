import json
import numpy as np
import cv2
import os

def convert_label_studio_json_to_masks(json_path, output_dir, label_value=255):
    """
    Converte anotações de polígono do Label Studio (JSON) em máscaras PNG.

    Args:
        json_path (str): Caminho para o arquivo JSON exportado do Label Studio.
        output_dir (str): Diretório para salvar as máscaras PNG geradas.
        label_value (int): Valor do pixel para a classe anotada (255 para branco).
    """
    # Cria o diretório de saída se ele não existir
    os.makedirs(output_dir, exist_ok=True)

    with open(json_path, 'r') as f:
        tasks = json.load(f)

    print(f"✅ Arquivo JSON carregado. Processando {len(tasks)} tarefas...")

    for task in tasks:
        # Extrai o nome do arquivo para usar no nome da máscara de saída
        # Ex: de '/data/upload/6/a8df3ee2-video9-frame0-00-48.01.jpg' para 'a8df3ee2-video9-frame0-00-48.01'
        image_url = task.get('data', {}).get('image')
        if not image_url:
            print(f"⚠️ Tarefa {task.get('id', 'N/A')}: Sem caminho de imagem. Pulando.")
            continue
            
        annotations = task.get('annotations', [])
        if not annotations:
            continue
            
        original_width, original_height = None, None
        all_polygons = []

        # Itera sobre todas as anotações e polígonos
        for annotation in annotations:
            for result in annotation.get('result', []):
                # Verifica se é uma anotação de polígono
                if result.get('type') == 'polygonlabels':
                    
                    # Obtém as dimensões originais (necessárias para escalonar as coordenadas %)
                    original_width = result.get('original_width')
                    original_height = result.get('original_height')
                    
                    if original_width is None or original_height is None:
                        continue
                        
                    normalized_points = result['value']['points']
                    
                    # Converte os pontos de porcentagem (0-100) para coordenadas de pixel (0-W/H)
                    polygon_points = []
                    for x_norm, y_norm in normalized_points:
                        x_pixel = int(x_norm * original_width / 100)
                        y_pixel = int(y_norm * original_height / 100)
                        polygon_points.append([x_pixel, y_pixel])
                    
                    all_polygons.append(np.array(polygon_points, dtype=np.int32))

        # Se houver polígonos válidos, cria e salva a máscara
        if all_polygons and original_width is not None:
            # Cria uma matriz preta (0) do tamanho da imagem original
            mask = np.zeros((original_height, original_width), dtype=np.uint8)
            
            # Desenha (preenche) todos os polígonos na máscara com o valor de pixel de fogo (255)
            cv2.fillPoly(mask, all_polygons, color=label_value)
            
            # Salva o arquivo PNG
            mask_filename = f"{image_url.split('/')[-1]}_mask.png"
            output_path = os.path.join(output_dir, mask_filename)
            cv2.imwrite(output_path, mask)
            print(f"  -> Máscara criada: {mask_filename}")

# --- CONFIGURAÇÃO E EXECUÇÃO ---

# 1. Defina o caminho para o seu arquivo JSON exportado do Label Studio
JSON_FILE = 'exported.json' # Certifique-se de que este caminho está correto

# 2. Defina o nome da pasta onde as máscaras PNG serão salvas
OUTPUT_FOLDER = 'output'

if __name__ == "__main__":
    convert_label_studio_json_to_masks(JSON_FILE, OUTPUT_FOLDER)
    print("\n✅ Processo concluído! Verifique a pasta 'masks_output'.")
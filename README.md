![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

# 🎥 GIFSKI GUI

**Uma interface gráfica moderna, rápida e intuitiva** para criar GIFs de alta qualidade usando **gifski** + **ffmpeg**.

Transforme seus vídeos em GIFs otimizados com preview em tempo real, corte preciso e configurações avançadas — tudo com poucos cliques.

![GIFSKI GUI - Interface Principal](https://github.com/casc1701/GIFSKI-GUI/blob/main/Screenshot_118.png?raw=true)

---

## ✨ Principais Recursos

- **Preview automático** — assim que você seleciona o vídeo, o preview é gerado automaticamente
- **Corte preciso** por frame inicial e final
- **Skip de frames** — reduza drasticamente o tamanho do GIF pulando frames
- **Controles avançados** de qualidade (Quality, Motion Quality, Lossy Quality)
- **Manter proporção** automática com sliders de largura e altura
- **Opção --fast** do gifski
- **Salvamento automático de configurações** — abre exatamente como você deixou da última vez
- Interface limpa com abas e design moderno (CustomTkinter)
- Diálogo nativo para salvar o GIF

---

## 📸 Capturas de Tela
![GIFSKI GUI - Interface Principal](https://github.com/casc1701/GIFSKI-GUI/blob/main/Screenshot_120.png?raw=true)

---

## 🚀 Como Usar

1. **Coloque os executáveis** na mesma pasta do programa, ou instale-os em outro lugar mas garanta que estão acessíveis via PATH:
   - `ffmpeg.exe`
   - `gifski.exe`

2. Execute o programa:
   ```bash
   python gera_gif.py
   
3. Clique em "📄 Selecionar Vídeo (.mp4)"

4. Ajuste as configurações nas abas (Corte & FPS, Qualidade, Dimensões)

5. Clique em Preview

6. Clique em "💾 Salvar GIF" quando estiver satisfeito



## ⚙️ Configurações Salvas

O programa lembra automaticamente:

* FPS
* Qualidades (Q, Motion, Lossy)
* Skip frames
* Dimensões e proporção
* Opção --fast


## 📋 Requisitos
 

Python 3.8 ou superior

Bibliotecas:
 ```bash
pip install customtkinter pillow
```

* ffmpeg e gifski (executáveis na mesma pasta ou no PATH)
* https://https://gif.ski/
* https://www.ffmpeg.org/



## 🛠️ Instalação Rápida
```bash
git clone https://github.com/casc1701/gifski-gui.git
```
```bash
cd gifski-gui
```
```bash
pip install customtkinter pillow
```
```bash
python gera_gif.py
```

## 📄 Licença
Este projeto está licenciado sob a GNU 2.

## 🙏 Agradecimentos

* gifski por criar a melhor ferramenta de conversão para GIF
* CustomTkinter pela bela interface
* Comunidade Python
* FFMPEG
* Grok


Feito com ❤️ por Cardoso & Grok, meu magnífico estagiário


import os
import subprocess

def tex_to_pdf(tex_file, pdf_file):
 
    if tex_file.endswith('.tex') and pdf_file.endswith('.pdf'):
        if os.path.exists(tex_file):
            file_path,file_name=os.path.split(tex_file)
            try:
                result = subprocess.run(
                        ['pdflatex','-interaction=nonstopmode', '-output-directory', '.', tex_file],
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE
                        )
                temp_pdf_file = file_name.replace('.tex', '.pdf')
                os.remove(file_name.replace('.tex', '.aux'))
                os.remove(file_name.replace('.tex', '.log'))
                os.rename(temp_pdf_file, pdf_file)
                print("pdf document sucessfully generated.")
            except Exception as e:
                print(str(e))
        else:
            raise Exception("tex file not found.") 
    else: 
        raise Exception("Arguments must be .tex and .pdf files paths")
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


from src.autoagentsai.utils.convertor import excel_to_csv_and_images

def main():
    excel_to_csv_and_images(
        input_file="playground/test_workspace/excel_with_images.xlsx",
        output_csv="playground/test_workspace/data_output.csv",
        img_dir="playground/test_workspace/img"
    )

if __name__ == "__main__":
    main()
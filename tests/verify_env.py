import sys
import torch
import fastapi
import transformers

def test_environment():
    print(f"QA: Verifierar miljö...")
    print(f" - Python: {sys.version}")
    print(f" - Torch: {torch.__version__} (CUDA: {torch.cuda.is_available()})")
    print(f" - FastAPI: {fastapi.__version__}")
    print(f" - Transformers: {transformers.__version__}")
    print("QA: Miljöverifiering OK!")

if __name__ == "__main__":
    test_environment()

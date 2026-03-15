import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image

class DocumentGatekeeper:
    def __init__(self, model_weights_path=None):
        # Load a lightweight ResNet18
        self.model = models.resnet18(pretrained=True)
        # Modify the final layer for binary classification: 0 = Scan (Xray/MRI), 1 = Document (Text)
        num_ftrs = self.model.fc.in_features
        self.model.fc = torch.nn.Linear(num_ftrs, 2)
        
        # If you train this later, you'd load your custom weights here
        if model_weights_path:
            self.model.load_state_dict(torch.load(model_weights_path))
            
        self.model.eval()
        
        # Standard image transformations for ResNet
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def route_document(self, image_path):
        """Returns 'SCAN' or 'DOCUMENT' based on visual features."""
        try:
            image = Image.open(image_path).convert('RGB')
            input_tensor = self.transform(image).unsqueeze(0)
            
            with torch.no_grad():
                output = self.model(input_tensor)
                _, predicted = torch.max(output, 1)
                
            # For this baseline, we assume 0 is Scan, 1 is Document
            return "DOCUMENT" if predicted.item() == 1 else "SCAN"
        except Exception as e:
            return f"Error processing image: {str(e)}"
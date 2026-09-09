import torch

class ActivationTracker:
    """
    Model ki kisi bhi layer pe 'hook' laga deta hai, taaki jab bhi
    model chale, us layer ka output automatically capture ho jaye -
    bina humein manually kuch nikaalna pade.
    """

    def __init__(self, model, layer_name):
        self.model = model
        self.layer_name = layer_name
        self.captured_activations = None
        self.handle = None

    def _hook_function(self, module, input_data, output_data):
        """Ye function PyTorch khud call karta hai jab layer chalti hai."""
        self.captured_activations = output_data.detach().numpy()

    def attach(self):
        """Hook ko layer se jodo."""
        layer = dict(self.model.named_modules())[self.layer_name]
        self.handle = layer.register_forward_hook(self._hook_function)

    def detach(self):
        """Hook ko hata do (jab kaam ho jaye)."""
        if self.handle is not None:
            self.handle.remove()

    def __enter__(self):
        self.attach()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.detach()


if __name__ == "__main__":
    import torch.nn as nn

    # ek chhota test model banate hain, sirf hooks test karne ke liye
    class SimpleModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.layer1 = nn.Linear(5, 3)

        def forward(self, x):
            return self.layer1(x)

    model = SimpleModel()
    tracker = ActivationTracker(model, "layer1")

    tracker.attach()
    test_input = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
    output = model(test_input)
    tracker.detach()

    print("Model output       :", output.detach().numpy().round(2))
    print("Hook ne pakda      :", tracker.captured_activations.round(2))
    print("Dono same hain?    :", (output.detach().numpy().round(2) == tracker.captured_activations.round(2)).all())
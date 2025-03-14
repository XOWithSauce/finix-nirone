import numpy as np
import tflite_runtime.interpreter as tflite

class TFLiteModel:
    def __init__(self, model_path: str):
        self.interpreter = tflite.Interpreter(model_path)
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def predict(self, data: list):
        features = np.expand_dims(np.array(data, dtype=np.float32), axis=0)
        for i in features:
            print(type(i))
        self.interpreter.set_tensor(self.input_details[0]["index"], features)
        self.interpreter.invoke()
        return self.interpreter.get_tensor(self.output_details[0]["index"])

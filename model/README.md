# Tensorflow Serving Compatible AI Model

## Overview
This documentation provides a high-level guide to using the AI model for textile classification. It covers the requirements for training data, model architecture, and deployment options for TensorFlow Serving and TensorFlow Lite.

### Directory Structure
The training data must be present in the model/data directory. The data files should adhere to the following format:

### Data Format
- Each file should be a JSON file containing the features measured across the NIR spectrum.
- The features must be a list of 512 floating point values.
- The file name should include a label indicating the fabric type, for example:
    - pes_123.json for Polyester (pes)
    - cotton_12.json for Cotton (cotton)
    - Other fabric types should follow a similar naming convention
        - Note: Requires code changes to data_parser.py to allow new samples to be used

#### Each JSON file should contain:

- username: The name of the user.
- timestamp: The timestamp of the measurement.
- sensor: The type of sensor used.
- data: An object containing:
- x: A list of 512 values representing the wavelengths (in nm) measured.
- y: A list of 512 values representing the scaled absorbance measurements.

Example JSON structure for pre-treated data:
```json
{
    "username":"JP",
    "timestamp":1590736552,
    "sensor":"NIRone",
    "data":{
        "x":[1550,1550.8, … (and 510 more)],
        "y":[0.4465654795510353,0.4477891991635261, … (and 510 more)]
    }
}
```

For raw data, the JSON file should contain:
- username: The name of the user.
- timestamp: The timestamp of the measurement.
- sensor: The type of sensor used.
- data: An object containing:
- dark: Sensor light cap covered with the backside of Nirone lambertian sample (Background radiation) with 0% light source
- reference: Against fully lambertian sample with 100% light source
- material: Material against sensor with 100% light source

- Note: In each subarray the y list is raw measurement results which are used to calculate the absorbance

```json
{
    "username":"JP",
    "timestamp":1590736552,
    "sensor":"NIRone",
    "data":{
        "dark": {
            "x": [1550, 1550.8, … (and 510 more)], // Wavelength index
            "y": [242.192, 239.600, … (and 510 more)], // Result from index
            "light": 0 // Sensor light level
        },
        "reference": { 
            "x": [1550, 1550.8, … (and 510 more)], // Wavelength index
            "y": [19032.800, 19065, … (and 510 more)], // Result from index
            "light": 100 // Sensor light level
        },
        "material": {
            "x": [1550, 1550.8, … (and 510 more)], // Wavelength index
            "y": [9828, 9840.212, … (and 510 more)], // Result from index
            "light": 100 // Sensor light level
        }
    }
}
```

### Sequential Network Architecture

#### Pipeline




## Jupyter Notebook (API compatibility)
>Make sure that Tensorflow-cpu (Windows) version matches the currently used Tensorflow serving package. (tensorflow_model_server --version) --> tensorflow-cpu --version has to match. Otherwise there will be errors while serving the compiled version.
>Currently using 2.14.0

## TFLite (Raspberry Pi Zero W1.1 compatibility)
>For the model to work with TFLite-runtime package, you must export the model as .tflite.
>For more information on serving this model, refer to the dedicated documentation: </br>
>[Inference documentation](../client/src/inference/README.md)

## CLI Support for MLM



# Helpful Notes and Memo for training / Tensorflow networks interpretation

### Training accuracy:
> High accuracy
> - This suggests the model is successfully learning patterns within the training data.

> Low accuracy
> - Underfitting: The model might not be complex enough to capture the underlying relationships in the data.
> - Issues with data or training process: There could be problems with data quality, preprocessing, or hyperparameter choices that are hindering learning.
### Training loss: 
> Lower loss
> - Generally indicates the model is making better predictions on the training data as it progresses through training.
> Higher loss:
> -  This suggests the model might not be learning effectively from the training data


### Validation accuracy:
> High accuracy
> - Model effectively learned patterns from the training data and generalizes well to unseen examples

> Low accuracy:
> - Suggests the model might be underfitting (not learning enough) or overfitting (memorizing training data but failing to generalize).

### Validation loss:
> Lower loss
> - Generally indicates better model performance on the validation set.
> Higher loss
> -  Suggests potential issues like underfitting or overfitti

#### Interpretation
> Training Accuracy Stalling While Validation Accuracy Improves:
>>   This could indicate the model is starting to overfit to the training data.
>>   The model might be memorizing specific details rather than learning generalizable patterns.
>>   Techniques like regularization or data augmentation can help address this.

> Training Loss Plateaus Early or Becomes Very Small:
>> This, along with high training accuracy, can be a sign of overfitting.
>> The model might have memorized the training data and stopped learning effectively.

> Validation Metrics Not Improving or Decreasing
>>  This suggests the model might be struggling to learn from the data
>>  It could be underfitting due to insufficient model complexity or issues with data quality or preprocessing.ng.
>>

## Pruning
>> Provided by model optimization library
>> Gradually zeroes out model weights during the training
>> During inference, zero value weights can be skipped -> increased performance (with low acc loss)
>> 
>> Pruning should be gradually applied during training to preserve initially learned connections
>> Large accuracy drops (over .30) indicate loss of meaningful connections within the network

## Confusion matrix
>> Contains a 3x3 prediction state calculation
>> Where for each label we calculate the prediction result

>> True Positive (For being correct when predicted correct)
>> True Negative (For being incorrect when predicted correct)
>> False Positive (For being correct when predicted incorrect)
>> False Negative (For being incorrect when predicted incorrect)


>>For multiclass classification problems
>>>The confusion matrix should show great proportion of samples within the 0,0 1,1 and 2,2 for correctly predicted instances
>>>![alt text](image.png)

For class 0:
| True/Predicted | Class 0       | Class 1       | Class 2       |
|----------------|---------------|---------------|---------------|
| **Class 0**    | TP (61)       | FN (13)       | FN (0)        |
| **Class 1**    | FP (0)        | TP (16)       | FN (62)       |
| **Class 2**    | FP (0)        | FP (1)        | TP (57)       |


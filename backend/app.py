from flask import Flask
import os
import uuid
import urllib
import tensorflow as tf
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from flask import Flask, render_template, request, send_file
from tensorflow.keras.preprocessing.image import load_img, img_to_array

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = load_model(os.path.join(BASE_DIR, 'model.hdf5'))


ALLOWED_EXT = set(['jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXT


classes = ['low fresh below best', 'low fresh best', 'low fresh poor', 'low withered below best',
           'low withered best', 'low withered poor']


def predict(filename, model):
    img = load_img(filename, target_size=(150, 150))
    img = img_to_array(img)
    img = img.reshape(-1, 150, 150, 3)

    img = img.astype('float32')
    img = img/255.0
    result = model.predict(img)

    dict_result = {}
    for i in range(6):
        dict_result[result[0][i]] = classes[i]

    res = result[0]
    res.sort()
    res = res[::-1]
    prob = res[:3]

    prob_result = []
    class_result = []
    for i in range(3):
        prob_result.append((prob[i]*100).round(2))
        class_result.append(dict_result[prob[i]])

    return class_result, prob_result

def predict_is_tea_leaf(img_path, model):
    # Load the image
    img = tf.keras.preprocessing.image.load_img(img_path, target_size=(150, 150))

    # Convert the image to a numpy array
    img_array = tf.keras.preprocessing.image.img_to_array(img)

    # Reshape the array to match the input shape of the model
    img_array = np.expand_dims(img_array, axis=0)

    # Preprocess the input
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)

    # Make the prediction
    predictions = model.predict(img_array)

    # Extract the output
    prediction = predictions[0][0]

    # Return True if the image contains a tea leaf and False otherwise
    if prediction < 0.5:
        return False
    else:
        return True
    
@app.route('/')
def home():
    return "this is home"


@app.route('/success', methods=['GET', 'POST'])
def success():
    error = ''
    target_img = os.path.join(os.getcwd(), 'static/images')
    if request.method == 'POST':
        if (request.form):
            link = request.form.get('link')
            try:
                resource = urllib.request.urlopen(link)
                unique_filename = str(uuid.uuid4())
                filename = unique_filename+".jpg"
                img_path = os.path.join(target_img, filename)
                output = open(img_path, "wb")
                output.write(resource.read())
                output.close()
                img = filename

                class_result, prob_result = predict(img_path, model)
                is_tea_leaf = predict_is_tea_leaf(img_path, model)

                predictions = {
                    "class1": class_result[0],
                    "class2": class_result[1],
                    "class3": class_result[2],
                    "prob1": prob_result[0],
                    "prob2": prob_result[1],
                    "prob3": prob_result[2],
                    "isTeaLeaf": True,
                    "message": "This is a tea leaf",
                }

            except Exception as e:
                print(str(e))
                error = 'This image from this site is not accesible or inappropriate input'

            if is_tea_leaf is False:
                predictions = {
                    "class1": "Please Enter a Tea Leaf and Proceed",
                    "class2": "Please Enter a Tea Leaf and Proceed",
                    "class3": "Please Enter a Tea Leaf and Proceed",
                    "prob1": "Please Enter a Tea Leaf and Proceed",
                    "prob2": "Please Enter a Tea Leaf and Proceed",
                    "prob3": "Please Enter a Tea Leaf and Proceed",
                    "isTeaLeaf": False,
                    "message": "Please enter a leaf and try again",
                }

            if (len(error) == 0):
                return predictions
            else:
                return error

        elif (request.files):
            file = request.files['file']
            if file and allowed_file(file.filename):
                file.save(os.path.join(target_img, file.filename))
                img_path = os.path.join(target_img, file.filename)
                img = file.filename

                class_result, prob_result = predict(img_path, model)
                is_tea_leaf = predict_is_tea_leaf(img_path, model)

                predictions = {
                    "class1": class_result[0],
                    "class2": class_result[1],
                    "class3": class_result[2],
                    "prob1": prob_result[0],
                    "prob2": prob_result[1],
                    "prob3": prob_result[2],
                    "isTeaLeaf": True,
                    "message": "This is a tea leaf",
                }

            else:
                error = "Please upload images of jpg , jpeg and png extension only"

            if is_tea_leaf is False:
                predictions = {
                    "class1": "Please Enter a Tea Leaf and Proceed",
                    "class2": "Please Enter a Tea Leaf and Proceed",
                    "class3": "Please Enter a Tea Leaf and Proceed",
                    "prob1": "Please Enter a Tea Leaf and Proceed",
                    "prob2": "Please Enter a Tea Leaf and Proceed",
                    "prob3": "Please Enter a Tea Leaf and Proceed",
                    "isTeaLeaf": False,
                    "message": "Please enter a leaf and try again",
                }
                
            if (len(error) == 0):
                return predictions
            else:
                return error

    else:
        return "hey"


if __name__ == "__main__":
    app.run(debug=True)


@app.route('/hello/', methods=['GET', 'POST'])
def welcome():
    return "Hello World!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=105)

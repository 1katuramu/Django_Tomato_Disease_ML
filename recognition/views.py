from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .models import TomatoImage
import tensorflow as tf
import numpy as np
import logging
import os

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def recognition(request):
    context = {}
    if request.method == 'POST' and request.FILES.get('test_image'):
        try:
            uploaded_file = request.FILES['test_image']
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_url = fs.url(filename)
            file_path = fs.path(filename)
            
            context['test_image_url'] = file_url

            if 'predict' in request.POST:
                prediction = model_prediction(file_path)
                if prediction is None:
                    context['error'] = 'There was an error with the prediction.'
                else:
                    context['prediction'] = prediction
                    
                    # Save the image and prediction to the database
                    tomato_image = TomatoImage(image=uploaded_file, prediction=prediction)
                    tomato_image.save()
                    
                    logger.info(f"Successful prediction for image: {filename}")
        
        except Exception as e:
            logger.error(f"Error in recognition view: {e}")
            context['error'] = 'There was an error processing the file.'
    else:
        logger.info("Recognition page accessed without file upload")

    return render(request, 'recognition.html', context)

def model_prediction(image_path):
    try:
        model = tf.keras.models.load_model(r'C:\Users\edgar\Desktop\tomato_recognition_system\trained_model.h5')
        image = tf.keras.utils.load_img(image_path, target_size=(128, 128))
        input_arr = tf.keras.utils.img_to_array(image)
        input_arr = np.array([input_arr])  # Convert single image to batch
        predictions = model.predict(input_arr)
        result_index = np.argmax(predictions)
        class_names = ['Reject', 'Ripe', 'Unripe']
        return class_names[result_index]
    except FileNotFoundError as e:
        logger.error(f"Model file not found: {e}")
        return None
    except Exception as e:
        logger.error(f"Error during model prediction: {e}")
        return None
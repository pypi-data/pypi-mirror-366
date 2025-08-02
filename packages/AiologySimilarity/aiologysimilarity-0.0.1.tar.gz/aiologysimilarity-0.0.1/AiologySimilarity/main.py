import numpy as np
from cv2 import Mat



class Similarity:
    """
# 🔎 Similarity

Search and find any similarities between two words ,or images

## Quick start

This module has two functions :

`check_words` and `check_frams`
## ----------------------------------------------------
### 📄 check words function

This function is used to detect similarity between words ,and it gets three parameters

`words` -> you sould pass a list of words which you wanna detect any similarity in

`detect_words` -> you should pass a list of `detect words` which will compared with words in the `words` list

`sensivity` -> you should pass a sensivity value for algorithm (higher sensivity value improves the detection)

`penalty` -> used when algorithm can't work as well ,and return this value as similarity percentage (most usage with lower sensivity value)

💡 Tip : It supports any language !!

## ----------------------------------------------------
### 📷 check frame function

This function is used to detect similarity between two frames of images ,and it gets three parameters

`frame` -> you sould pass an `OPENCV` frame or a `NUMPY ndarray with 3 depths` which you wanna detect any similarity in

`main_frame` -> you sould pass an `OPENCV` frame or a `NUMPY ndarray with 3 depths` which will compared with words in the `words` list

`sensivity` -> you should pass a sensivity value for algorithm (higher sensivity value improves the detection)

## ----------------------------------------------------
### 📄 check words example
```
from AiologySimilarity import Similarity

similar = Similarity()

similar_words = ["Hello","hey","سلام","سلام علیکم"]
words = ["Hello","سلام"]

for word , similarity_percentage in similar.check_words(similar_words,words,50):
    print(word , similarity_percentage)
```

### 📷 check frame example
```
from AiologySimilarity import Similarity
from cv2 import imread

similar = Similarity()

frame1 = imread("YOUR_IMAGE_1")
frame2 = imread("YOUR_IMAGE_2")

similarity , similarity_percentage = similar.check_frames(frame1,frame2,100)
print(similarity , similarity_percentage)
```
    """
    def check_words(self,words : tuple[str] , detect_words : tuple[str] , sensivity : int,penalty : int = 50):
        """
## Check similarity of words

This function find any similarity between words ,then yield similar words with their similarity percentages

`check_words(self,words : tuple[str] , detect_words : tuple[str] , sensivity : int,penalty : int = 50)`

--yield--> `similar word , similarity percentages` 
        """
        if not (0 <= sensivity <= 100):
            raise Exception("The word detection sensivity should be between 0 and 100")
        
        if (any(words) == False) or (any(detect_words) == False):
            raise Exception("No words passed as parameter")

        count = 0

        for word in words:
            for detect_word in detect_words:

                if (sensivity * len(detect_word) / 100) <= len(word):
                    for letter in detect_word:
                        if letter in word:
                            count += 1

                if count != 0:
                    percentage = count * 100 / len(word)
                    if percentage == 100:
                        if word == detect_word:
                            yield word , detect_word , percentage
                        else:
                            yield word , detect_word , penalty
                    elif percentage < 100:
                        if percentage >= sensivity:
                            yield word , detect_word , percentage
                    else:
                        yield word , detect_word , penalty

                    count = 0

    def check_frames(self,frame : Mat,main_frame : Mat,sensivity : int):
        """
## Check similarity of frames

This function find any similarity between two frames ,then it returns similarity boolean with its similarity percentages

`check_frames(self,frame : Mat,main_frame : Mat,sensivity : int)`

--return--> `similarity boolean , similarity percentages` 
        """
        if not (0 <= sensivity <= 100):
            raise Exception("The frames detection sensivity should be between 0 and 100")

        try:
            if main_frame.shape != frame.shape:
                raise Exception("These two frames doesn't have the same size !! , resizing them to avoid lossing data")
        except:
            raise Exception("Invalid format type of a frame passed !!")

        similarity = False
        similarity_count = 0

        calculated_frame = np.subtract(
            1,np.divide(
                abs(np.subtract(frame,main_frame,dtype=np.int32)),
                255
            )
        )

        similarity_count = np.sum(list(map(lambda row : list(map(lambda pixel : sum(pixel) / 3,row)),calculated_frame)))

        similarity_percentage = similarity_count / (main_frame.shape[0] * main_frame.shape[1]) * 100
        if similarity_percentage >= sensivity:
            similarity = True
        
        return similarity , similarity_percentage
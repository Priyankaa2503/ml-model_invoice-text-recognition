# import necessary packages
from collections import namedtuple
import pytesseract
import argparse
import imutils
import cv2

def cleanup_text(text):
	# strip out non-ASCII text 
	return "".join([c if ord(c) < 128 else "" for c in text]).strip()

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to input image")
args = vars(ap.parse_args())

# create a named tuple which we can use to create locations of the
# input document
OCRLocation = namedtuple("OCRLocation", ["id", "bbox"])
# define the locations of each area of the document we wish to OCR
OCR_LOCATIONS = [
	OCRLocation("name", (2400, 740, 200, 40)),
	OCRLocation("Date", (2400, 690, 200, 50)),
	OCRLocation("email", (255, 790, 550, 40)),
	OCRLocation("address", (130, 663, 1170, 50)),
	OCRLocation("Plan", (350, 1130, 890, 80)),
	OCRLocation("Amount", (1550, 1240, 150, 50))
]

# load the input image
print("[INFO] loading images...")
img = cv2.imread(args["image"])
image = img.copy()


# initialize a results list to store the document OCR parsing results
print("[INFO] OCR'ing document...")
parsingResults = []
# loop over the locations of the document we are going to OCR
for loc in OCR_LOCATIONS:
	# extract the OCR ROI from the image
	(x, y, w, h) = loc.bbox
	roi = image[y:y + h, x:x + w]
	# OCR the ROI using Tesseract
	rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
	text = pytesseract.image_to_string(rgb)
    
    # break the text into lines and loop over them
	for line in text.split("\n"):
		# if the line is empty, ignore it
		if len(line) == 0:
			continue
		lower = line.lower()
		parsingResults.append((loc, line))
            
# initialize a dictionary to store our final OCR results
results = {}

# loop over the results of parsing the document
for (loc, line) in parsingResults:
	# grab any existing OCR result for the current ID of the document
	r = results.get(loc.id, None)
	# if the result is None, initialize it using the text and location
	# namedtuple (converting it to a dictionary as namedtuples are not
	# hashable)
	if r is None:
		results[loc.id] = (line, loc._asdict())
	# otherwise, there exists an OCR result for the current area of the
	# document, so we should append our existing line
	else:
		# unpack the existing OCR result and append the line to the
		# existing text
		(existingText, loc) = r
		text = "{}\n{}".format(existingText, line)
		# update our results dictionary
		results[loc["id"]] = (text, loc)
        
cleaned_result = {}

# loop over the results
for (locID, result) in results.items():
	# unpack
	(text, loc) = result
	# display the OCR result
# 	print(loc["id"])
# 	print("=" * len(loc["id"]))
# 	print("{}\n\n".format(text))

	# extract the bounding box coordinates of the OCR location and
	# then strip out non-ASCII text using function "cleanup_text" defined above.
	(x, y, w, h) = loc["bbox"]
	clean = cleanup_text(text)
	cleaned_result[loc['id']] = clean
    
 	# we can draw the text on the output image using OpenCV
	# draw a bounding box around the text
	cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
	cv2.putText(image, clean, (x,y),
			cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

 

 # show the input and output images, resizing it such that they fit on our screen
print(cleaned_result)
cv2.imshow("Input", imutils.resize(img, width=700))
cv2.imshow("Output", imutils.resize(image, width=1000))
cv2.waitKey(0)
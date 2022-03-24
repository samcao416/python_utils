import cv2
import os
import glob

video_path_list = sorted(glob.glob(os.path.join("*.mp4")))

# rotate 90 clockwise
def RotateClockWise90(img):
    trans_img = cv2.transpose(img)
    new_img = cv2.flip(trans_img, 1)
    return new_img


# rotate 90 anticlockwise
def RotateAntiClockWise90(img):
    trans_img = cv2.transpose(img)
    new_img = cv2.flip(trans_img, 0)
    return new_img


for video_path in video_path_list:

    print("Processing ", video_path)

    if 'front' in video_path:
        clockwise = False
    
    elif 'back' in video_path:
        clockwise = True
    
    else:
        clockwise = None
    
    outdir = os.path.join(video_path + 'image')
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    video = cv2.VideoCapture(video_path)
    
    numFrame = 0
    while True:
        if video.grab():
            flag, frame = video.retrieve()
            if not flag:
                continue
            else:
                numFrame += 1
                image_path = os.path.join(outdir, '%4d' %(numFrame) + ".jpg")
                if clockwise == True:
                    frame = RotateClockWise90(frame)
                elif clockwise == False:
                    frame = RotateAntiClockWise90(frame)
                else:
                    pass
                cv2.imwrite(image_path, frame)
                
        else:
            break

print("Done.")
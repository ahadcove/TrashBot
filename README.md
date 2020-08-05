cd into the ML directory before copy and pasting these commands
`cd ML`

First download your images from google using [google_images_download](https://github.com/hardikvasa/google-images-download)
`python3 utils/google_images_download.py --keywords "republic services truck" --limit 100 --output_directory data/images --chromedriver loc/to/chromedriver`

After you download the images let's move the images from the download folder to `data/images` for now.
Let's convert all of our images to jpg before we continue.
`python3 utils/imgconvert.py --folder data/images`

We'll need to annotate our images.
set your bounding boxes for your images. We'll use [LabelImg](https://github.com/tzutalin/labelImg)
After compiling LabelImg from the link above, you can open it with:
`python3 path/to/labelImg.py data/images`

After we're done labeling our images you'll have a bunch of xml files. We need to convert the XML files that labelimg created to csv. But before we do that let's split up our images into two different folders: train and test.
`mkdir data/train && mkdir data/test`

Also create a `open-images-model-labels.txt` file inside data/ as well and input all of your class names. 1 per line:
`touch open-images-model-labels.txt`
```
BACKGROUND
garbage_truck
```

As well as a labels.txt file:
`labels.txt`
```
garbage_truck
```


A good rule of thumb is to put 80% of the images inside train and 20% inside test.
Make sure when splitting up the images you copy the xml files as well.

Now we can run xml2csv:
`python3 utils/xml2csv.py --folder data/ --dest data/`

We're all set to start training now
Let's first download the pretrained mobilenet model from Nvidia since they so kindly already did most of the work for us:
`wget https://nvidia.box.com/shared/static/djf5w54rjvpqocsiztzaandq1m3avr7c.pth -O train/models/mobilenet-v1-ssd-mp-0_675.pth`

We'll be using the [Pytorch-ssd](https://github.com/qfgaohao/pytorch-ssd) library to make things really simple for us.
`python3 ssd-train/train_ssd.py --dataset_type open_images --datasets data --net mb1-ssd --pretrained_ssd ssd-train/models/mobilenet-v1-ssd-mp-0_675.pth --num_epochs 30 --batch_size 4 --num_workers=0`

Now we should have our model. We can now test it out on an image:
`python3 ssd-train/run_ssd_example.py mb1-ssd data/mb1-ssd-Epoch-29-Loss-1.8117772539456685.pth data/open-images-model-labels.txt data/test/86.refuse-garbage.jpg`

You'll now see your output image at `data/output.jpg` with the image labeled.

From here we're going to be converting things so we can use it on our Nvidia Jetson devices.

First we'll convert our model from pytorch to onnx so we can load it with TensorRT on our Jetson
`python3 ssd-train/onnx_export.py --model-dir=data --labels=open-images-model-labels.txt`


We will send these files over to the Jetson:
```
data/mb1-ssd-Epoch-29-Loss-1.8117772539456685.pth
data/open-images-model-labels.txt
detectnet.py
```

Build [Jetson-Inference](https://github.com/dusty-nv/jetson-inference/blob/master/docs/building-repo-2.md#compiling-the-project) on your Jetson device before continuing

Tip: If you want to run commands from ssh but display it on the screen of the jetson, run: `export DISPLAY=:0` before running the script


We're now ready to test some images with our new TensorRT model.

cd into the Run directory
`cd ../Run`

If you're running this with a Pi, copy the whole Run/pi directory to your Pi and start the flask server on your pi

Now on the jetson you can run:
`python3 watch_cam_rt.py --net_type=ssd-mobilenet-v2 --model=data/ssd-mobilenet.onnx --labels=data/open-images-model-labels.txt --input=/dev/video0 --show`


Or without TensorRT:
`python3 watch_cam.py --net_type=mb1-ssd --model_path=data/mb1-ssd-Epoch-29-Loss-1.8117772539456685.pth --label_path=data/open-images-model-labels.txt --input=0 --show`

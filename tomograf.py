import math
import skimage as sk
import numpy as np
import pydicom as dic
import datetime


def normalize(im): # normalizacja obrazu
  norm = np.zeros(shape=(im.shape))
  im_max = im.max()
  im_min = 0
  for x in range(im.shape[0]):
    norm[x] = np.interp(im[x], (im_min, im_max), (0, 255))
  return norm

def loadImage(imgPath): # ładuje obrazek
  im = sk.io.imread(imgPath, as_gray=True)
  im = normalize(im)
  return im

def bresenham(img,x1,y1,x2,y2): # algorytm Bresenhama, zwraca średnią jasność
  max_x = len(img)
  max_y = len(img[0])
  sum = 0
  n = 0
  x = x1
  x_inc = 1 # inkrement
  dx = x2 - x1 # przesunięcie
  y = y1
  y_inc = 1
  dy = y2 - y1
  if x1>=x2: # rysujemy w lewo, zamiast w prawo
    x_inc = -1
    dx = x1 - x2
  if y1>=y2: # rysujemy w dół, zamiast w górę
    y_inc = -1
    dy = y1 - y2
  if dx > dy: # oś wiodąca OX
    ep_inc_a = 2*(dy-dx)
    ep_inc_b = 2*dy
    ep = ep_inc_b - dx # błąd (odchylenie od współrzędnych całkowitych)
    while x!=x2:
      if not(x>=max_x or y>=max_y or x<0 or y<0): # sprawdzamy czy nie jesteśmy poza obrazkiem
        sum += img[x-1][y-1]
        n += 1
      if ep>=0:
        y += y_inc
        ep += ep_inc_a
      else:
        ep += ep_inc_b
      x += x_inc
  else: # oś wiodąca OY
    ep_inc_a = 2*(dx-dy)
    ep_inc_b = 2*dx
    ep = ep_inc_b - dy # błąd (odchylenie od współrzędnych całkowitych)
    x = x1
    while y!=y2:
      if not(x>=max_x or y>=max_y or x<0 or y<0):
        sum += img[x-1][y-1]
        n += 1
      if ep>=0:
        x += x_inc
        ep += ep_inc_a
      else:
        ep += ep_inc_b
      y += y_inc
  try:
    a = sum/n # średnia jasność pikseli w rysowanej linii
  except: 
    a = 0 # Uroki okręgu opisanego ¯\_(ツ)_/¯
  return a

def radonTransform(img,t,img_label, emitterRange = 180, numOfDetectors = 180, numOfScans = 180, alphaShift = 2, animating = False, animationInterval = 20):
  t.set_label_progress("Transformata Radona")
  alphaShift = math.radians(alphaShift)
  center = (len(img)//2, len(img[0])//2)
  R = max(center) * math.sqrt(2)
  alpha = (2*math.pi*90)/360 # alpha emitera, zaczynamy od 90 stopni myślę i tu wystarczy potem dodawać to przesunięcie
  phi = (2*math.pi*emitterRange)/360 # kąt rozwarcia dla detektorów
  sinogram = np.zeros(shape=(numOfScans,numOfDetectors))
  for scan in range(numOfScans): # dla każdego skanu
    t.progress((scan/numOfScans)*100)
    # tutaj dla wzyznaczanych współrzędnych za każdym razem odnoszę się do środka, aby nie robić potem przesunięć
    xe = center[0] + round(R * math.cos(alpha))
    ye = center[1] - round(R * math.sin(alpha))
    for det in range(numOfDetectors): # dla każdego detektora
      xd = center[0] + round(R * math.cos(alpha+math.pi-phi/2 + det*phi/(numOfDetectors-1)))
      yd = center[1] - round(R * math.sin(alpha+math.pi-phi/2 + det*phi/(numOfDetectors-1)))
      sinogram[scan][det] = bresenham(img,xe,ye,xd,yd) # rysujemy linię od emitera do detektora
    alpha += alphaShift # wykonujemy przesunięcie
    if animating and scan % animationInterval == 0: # sekcja animacji
      t.showImage(normalize(sinogram),img_label)
  return normalize(sinogram)

def inverseBresenham(max_x,max_y,x1,y1,x2,y2): # zwraca koordynaty pikseli między emiterem a detektorem
  coords = []
  x = x1
  x_inc = 1 # inkrement
  dx = x2 - x1 # przesunięcie
  y = y1
  y_inc = 1
  dy = y2 - y1
  if x1>=x2: # rysujemy w lewo, zamiast w prawo
    x_inc = -1
    dx = x1 - x2
  if y1>=y2: # rysujemy w dół, zamiast w górę
    y_inc = -1
    dy = y1 - y2
  if dx > dy: # oś wiodąca OX
    ep_inc_a = 2*(dy-dx)
    ep_inc_b = 2*dy
    ep = ep_inc_b - dx # błąd (odchylenie od współrzędnych całkowitych)
    while x!=x2:
      if not(x>=max_x or y>=max_y or x<0 or y<0):
        coords.append((x-1,y-1))
      if ep>=0:
        y += y_inc
        ep += ep_inc_a
      else:
        ep += ep_inc_b
      x += x_inc
  else: # oś wiodąca OY
    ep_inc_a = 2*(dx-dy)
    ep_inc_b = 2*dx
    ep = ep_inc_b - dy # błąd (odchylenie od współrzędnych całkowitych)
    x = x1
    while y!=y2:
      if not(x>=max_x or y>=max_y or x<0 or y<0):
        coords.append((x-1,y-1))
      if ep>=0:
        x += x_inc
        ep += ep_inc_a
      else:
        ep += ep_inc_b
      y += y_inc
  return coords

def inverseRadonTransform(sinogram, img,t,img_label, emitterRange = 180, numOfDetectors = 180, numOfScans = 180, alphaShift = 2, animating = False, animationInterval=20):
  t.set_label_progress("Odwrotna Transformata Radona")
  alphaShift = math.radians(alphaShift)
  center = (img.shape[0]//2, img.shape[1]//2)
  R = max(center) * math.sqrt(2)
  alpha = (2*math.pi*90)/360 # alpha emitera, zaczynamy od 90 stopni myślę i tu wystarczy potem dodawać to przesunięcie
  phi = (2*math.pi*emitterRange)/360 # kąt rozwarcia dla detektorów
  reconstructed = np.zeros(shape=img.shape)
  for scan in range(numOfScans): # dla każdego skanu (wzmocnienia)
    t.progress((scan/numOfScans)*100)
    # tutaj dla wzyznaczanych współrzędnych za każdym razem odnoszę się do środka, aby nie robić potem przesunięć
    xe = center[0] + round(R * math.cos(alpha))
    ye = center[1] - round(R * math.sin(alpha))
    for det in range(numOfDetectors): # dla każdego detektora
      xd = center[0] + round(R * math.cos(alpha+math.pi-phi/2 + det*phi/(numOfDetectors-1)))
      yd = center[1] - round(R * math.sin(alpha+math.pi-phi/2 + det*phi/(numOfDetectors-1)))
      coords = inverseBresenham(img.shape[0], img.shape[1],xe,ye,xd,yd) # wyznaczamy linię między emiterem a detektorem
      reconstructed[tuple(np.transpose(coords))] += sinogram[scan][det] # wzmacniamy piksele wyznaczonej linii o odpowiednią średnią
    alpha += alphaShift # wykonujemy przesunięcie
    if animating and scan % animationInterval == 0: # sekcja animacji
      t.showImage(normalize(reconstructed),img_label)
      mse, rmse = calcRMSE(img,normalize(reconstructed))
      t.set_label_progress(f"Odwrotna Transformata Radona\nRMSE: {rmse:.4f}")
      print(f"\nBłąd średniokwadratowy wynosi {mse:.2f}")
      print(f"RMSE wynosi {rmse:.2f}")
  mse, rmse = calcRMSE(img,normalize(reconstructed))
  t.set_label_progress(f"Odwrotna Transformata Radona\nRMSE: {rmse:.4f}")
  return normalize(reconstructed)

def filtr(sinogram,t,img_label, animating = False): # filtr splotowy
  t.set_label_progress("Filtrowanie")
  result = []
  for i in range(1,11): # tworzymy połowę maski
    if i%2==0:
      result.append(0)
    else:
      result.append(-4/pow(math.pi,2)/pow(i,2))
  res2 = result.copy()
  result.reverse() # wykorzystujemy odbicie lustrzane
  kernel = result + [1] + res2 # tworzymy maskę o rozmiarze 21
  for i in range(sinogram.shape[0]):
    t.progress((i/sinogram.shape[0])*100)
    sinogram[i, :] = np.convolve(sinogram[i, :], kernel, mode="same") # wykonujemy splot
    if animating:
      t.showImage(normalize(sinogram),img_label,flag=True)

def calcRMSE(im1, im2): # obliczanie RMSE
  mse = np.square(np.subtract(im1, im2)).mean()
  return (mse, math.sqrt(mse)) # (mse, rmse)

def jpg_to_dcm(reconstructed,name="BRAK",patient_id="0",date="",comment="BRAK"): # zapisywanie obrazu do dicom
  # Meta tagi
  file_meta = dic.dataset.FileMetaDataset()
  file_meta.MediaStorageSOPClassUID = dic.uid.UID('1.2.840.10008.5.1.4.1.1.2')
  file_meta.MediaStorageSOPInstanceUID = dic.uid.generate_uid()
  file_meta.ImplementationClassUID = dic.uid.UID("1.2.826.0.1.3680043.8.498.1")
  dcm = dic.dataset.FileDataset("output.dcm", {}, file_meta=file_meta, preamble=b"\0" * 128)
  dcm.file_meta.TransferSyntaxUID = dic.uid.ImplicitVRLittleEndian
  dcm.is_little_endian = True
  dcm.is_implicit_VR = True

  # Zapisujemy wybrane dane o pacjencie i badaniu
  dt = datetime.datetime.now()
  if date == "":
    dcm.StudyDate = dt.strftime('%Y%m%d')
    dcm.ContentDate = dt.strftime('%Y%m%d')
  else:
    dcm.StudyDate = date
    dcm.ContentDate = date
  dcm.StudyTime = dt.strftime('%H%M%S')
  timeStr = dt.strftime('%H%M%S.%f')
  dcm.ContentTime = timeStr
  dcm.PatientName = name
  dcm.PatientID = patient_id
  dcm.StudyID = "1234"
  dcm.SeriesNumber = "1"
  dcm.PatientComments = comment

  # Generijemy unikatowe ID instancji
  dcm.SOPInstanceUID = dic.uid.generate_uid()
  dcm.SeriesInstanceUID = dic.uid.generate_uid()
  dcm.StudyInstanceUID = dic.uid.generate_uid()
  dcm.FrameOfReferenceUID = dic.uid.generate_uid()

  # Parametry obrazu
  dcm.ImageType = ["ORIGINAL", "PRIMARY", "AXIAL"]
  dcm.Modality = "CT"
  dcm.Rows = reconstructed.shape[0]
  dcm.Columns = reconstructed.shape[1]
  dcm.BitsAllocated = 8
  dcm.BitsStored = 8
  dcm.HighBit = dcm.BitsStored - 1
  dcm.SamplesPerPixel = 1
  dcm.PhotometricInterpretation = 'MONOCHROME2'
  dcm.PixelRepresentation = 0
  dcm.PixelData = reconstructed.astype(np.uint8).tobytes() # piksele obrazka

  # Prywatne bloki do zapisania własnych danych, np.: komentarza
  block = dcm.private_block(0x000b, "PUT 151785 151741", create=True)
  block.add_new(0x01, "SH", comment)
  dcm.save_as("output.dcm", write_like_original=False)
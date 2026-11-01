"""Optional OpenCV preprocessing; source images are never overwritten."""
from pathlib import Path

def preprocess_image(source: str | Path, destination: str | Path, grayscale: bool = True,
                     denoise: bool = True, deskew: bool = True) -> Path:
    try:
        import cv2
        import numpy as np
    except ImportError as exc: raise RuntimeError("Install OpenCV with pip install -e '.[ocr]'") from exc
    src,dst=Path(source),Path(destination)
    image=cv2.imread(str(src))
    if image is None: raise ValueError(f"Cannot decode image: {src}")
    if grayscale: image=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    if denoise:
        image=cv2.fastNlMeansDenoising(image,None,8,7,21) if image.ndim==2 else cv2.fastNlMeansDenoisingColored(image,None,6,6,7,21)
    if deskew and image.ndim==2:
        points=np.column_stack(np.where(image<245))
        if len(points)>100:
            angle=cv2.minAreaRect(points.astype("float32"))[-1]
            angle=-(90+angle) if angle < -45 else -angle
            if abs(angle)>0.15:
                height,width=image.shape[:2]
                matrix=cv2.getRotationMatrix2D((width/2,height/2),angle,1.0)
                image=cv2.warpAffine(image,matrix,(width,height),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
    dst.parent.mkdir(parents=True,exist_ok=True)
    if not cv2.imwrite(str(dst),image): raise OSError(f"Could not write: {dst}")
    return dst

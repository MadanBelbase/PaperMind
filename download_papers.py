"""Downloads the open-access PDFs, saved as '<paper title>.pdf'. Run: python download_papers.py"""
import re, os, urllib.request
A=lambda x:"https://arxiv.org/pdf/"+x
CVF="https://openaccess.thecvf.com/content/"
PAPERS=[
("CNN for License Plate Motion Deblurring",A("1602.07873")),
("A Dataset and Model for Realistic License Plate Deblurring",A("2404.13677")),
("VRAE - Vertical Residual Autoencoder for License Plate Denoising and Deblurring",A("2509.08392")),
("SNIDER - Single Noisy Image Denoising and Rectification for Improving License Plate Recognition",A("1910.03876")),
("Super-Resolution of License Plate Images Using Attention Modules and Sub-Pixel Convolution Layers",A("2305.17313")),
("Using Super-Resolution Imaging for Recognition of Low-Resolution Blurred License Plates",A("2403.15466")),
("Enhancing License Plate Super-Resolution - A Layout-Aware and Character-Driven Approach",A("2408.15103")),
("Toward Advancing License Plate Super-Resolution in Real-World Scenarios - A Dataset and Benchmark",A("2505.06393")),
("LPLC - A Dataset for License Plate Legibility Classification",A("2508.18425")),
("Robust Automatic Motorcycle Helmet Violation Detection for an Intelligent Transportation System",CVF+"CVPR2023W/AICity/papers/Tran_Robust_Automatic_Motorcycle_Helmet_Violation_Detection_for_an_Intelligent_Transportation_CVPRW_2023_paper.pdf"),
("An Effective Method for Detecting Violation of Helmet Rule for Motorcyclists",CVF+"CVPR2024W/AICity/papers/Chen_An_Effective_Method_for_Detecting_Violation_of_Helmet_Rule_for_CVPRW_2024_paper.pdf"),
("Real-Time Helmet Violation Detection in AI City Challenge 2023 with Genetic Algorithm-Based Hyperparameter Optimization",A("2304.09248")),
("Real-Time Helmet Violation Detection Using YOLOv5 and Ensemble Learning",A("2304.09246")),
("Next-gen traffic surveillance - AI-assisted mobile traffic violation detection system",A("2311.16179")),
("YOLO-LLTS - Real-Time Low-Light Traffic Sign Detection",A("2503.13883")),
("A New U-Net Based License Plate Enhancement Model in Night and Day Images","https://opus.lib.uts.edu.au/bitstream/10453/147963/3/A%20New%20U-Net%20Based%20License%20Plate%20Enhancement%20Model%20in%20Night%20and%20Day%20Images.pdf"),
("Optimasi Deteksi Pelanggaran Helm pada Traffic Light Berbasis YOLOv7 dan CLAHE","https://ejournal.raharja.ac.id/cerita/article/download/3883/2407/12237"),
]
MANUAL=["LPSRGAN (Neurocomputing 2024): https://wrap.warwick.ac.uk/183557/",
"Real-World LP Image SR via Domain-specific Degradation Modeling (IEEE CAI 2024): https://pure.ecnu.edu.cn/en/publications/real-world-license-plate-image-super-resolution-via-domain-specif/",
"Enhancement and LP detection in nighttime scenes using LDR images fusion (ICME-W 2014): https://dblp1.uni-trier.de/rec/conf/icmcs/PeiW14.html"]
os.makedirs("papers_pdf",exist_ok=True)
for t,u in PAPERS:
    fn=re.sub(r'[\\/:*?"<>|]','',t)[:150]+".pdf"
    try:
        d=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=60).read()
        assert d[:4]==b"%PDF"
        open(os.path.join("papers_pdf",fn),"wb").write(d); print("OK  ",fn)
    except Exception as ex:
        print("FAIL",fn,"->",u,ex)
print("\nDownload these manually:"); [print(" -",m) for m in MANUAL]

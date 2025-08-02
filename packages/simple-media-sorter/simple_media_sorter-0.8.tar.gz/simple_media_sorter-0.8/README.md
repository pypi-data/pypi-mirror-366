# Simple Media Sorter
![SMS](https://github.com/hanzo-hasashi/SimpleMediaSorter/blob/main/MediaSorter.png)
- Set of Python scripts to sort and rename media files...
- This mainly utilizes the EXIF plugin to extract metadata and perform operations accordingly.
- Useful when working on media files from different sources like merging local and Google Photos Takeout files.
- Please take a backup of your files before performing any action using the script!

## Configuration
The scripts require source & destination folders. Configure them in the config_media_sorter.py file:

- source_directory_para = r"C:\Users\admin\Desktop\Unsorted" #path to source folder
- destination_directory_para = r"C:\Users\admin\Desktop\Out" #path to destination folder

## Scripts
- [Copy Files.py](https://github.com/hanzo-hasashi/SimpleMediaSorter/blob/main/Copy%20Files.py): Copies files with specific extensions while maintaining the folder structure.
- [EXIF Search Move.py](https://github.com/hanzo-hasashi/SimpleMediaSorter/blob/main/EXIF%20Search%20Move.py): This searches for EXIF Tag "keyword" and moves them to a sub-folder.
- [EXIF Tags Copier.py](https://github.com/hanzo-hasashi/SimpleMediaSorter/blob/main/EXIF%20Tags%20Copier.py): This copies specified EXIF tags from files in the Source Directory to the Destination Directory. Files must be present in both folders with the same name.
- [EXIF Tags Extracter.py](https://github.com/hanzo-hasashi/SimpleMediaSorter/blob/main/EXIF%20Tags%20Extracter.py): This extracts specific EXIF tags from images & videos and stores them into a CSV file.
- [moveToFolder_IMG_VID_EXIF.py](https://github.com/hanzo-hasashi/SimpleMediaSorter/blob/main/moveToFolder_IMG_VID_EXIF.py): Use this script to move image & video files to "YYYY\MMYY" folder (example 2019\0119 January). For images, the date is extracted from the EXIF tag; for videos, this date is extracted from the QuickTime tag.
- [update_EXIF_Date_fromFileName.py](https://github.com/hanzo-hasashi/SimpleMediaSorter/blob/main/update_EXIF_Date_fromFileName.py): Use this script to extract DateTime from file (YYYYMMDD) and update it in the EXIF.
- [update_EXIF_Dates_fromSystemDates.py](https://github.com/hanzo-hasashi/SimpleMediaSorter/blob/main/update_EXIF_Dates_fromSystemDates.py): Use this script to copy SystemDate into EXIF Date tags.
- [update_File_Name_fromEXIF.py](https://github.com/hanzo-hasashi/SimpleMediaSorter/blob/main/update_File_Name_fromEXIF.py): Use this script to update filename.jpg to filename_Date_Time.jpg

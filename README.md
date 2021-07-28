# cy2003-cellcounting: cell_counting branch

This branch contains the different iterations of the cell counting model. For organisation, older versions of the model have been stored in the python notebook and existing `.py` files includes the more recent Blob Detection versions.

# Running the Python Notebook in Google Colab

## Getting Started with Google Colab

You will require a notebook (.ipynb) to run code from as the main point of interaction. In this case, it would be `cellcounting.ipynb`, which can be downloaded from this branch.
Download this notebook and save it into your Google Drive. Click and open it; Google should automatically redirect you to a Google Colab workspace.
Alternatively, you can also try it on Google Colab [here](https://colab.research.google.com/drive/1TpMPwQtW_eJPdbPZSXpPmW9fzbF1FXMI?authuser=0#scrollTo=s8lWMdy9MW0X).

### Mounting your Google Drive in the Google Colab workspace

A cell has been set up in the notebook to link your Google Drive to the workspace. This allows easy access to training data, model weights if stored on Google Drive. Saves local storage space and makes use of the free storage in Google Drive (15GB) and Colab (69GB). To run cell, press `Shift` + `Enter` as how Jupyter notebooks are used.

After mounting, you can retrieve whatever is needed by the path `/content/gdrive/MyDrive/<filepath>`

### Cloning the Repository into the workspace

Google Colab timeouts after 12 hours of continuous use and will not store your workspace data for you. This is why Google Drive is very handy as you can easily set up autosaving to the drive. You will need to remount the drive and reclone the Github repository everytime Google Colab timeouts and restarts but it is quite simple to setup.

Cells can be added to the main notebook to run functions from .py files from the repository. Remember to specify the branch name of the repository.

# Marriott Reparative Metadata Assessment Tool (MaRMAT)
The Marriott Reparative Metadata Assessment Tool (MaRMAT) is an open-source application created by librarians at the University of Utah’s J. Willard Marriott Library to help metadata practitioners flag various terms and phrases within metadata records using pre-curated and custom lexicons. MaRMAT is schema agnostic and supports library and museum professionals in assessing metadata for harmful, outdated, and otherwise problematic language in tabular metadata. In addition to reparative work, MaRMAT can be used to support broader metadata assessment and collections content analysis. Learn more about MaRMAT on our website: [www.marmatproject.org](https://marmatproject.org/).

## Table of Contents
1. [About](#1-about)

   1.1 [Features](#11-features)

   1.2 [The Lexicons](#12-the-lexicons)

2. [Installation](#2-installation)

   2.1 [Download](#21-download)

   2.2 [Dependencies](#22-dependencies)

   2.3 [Troubleshooting](#23-troubleshooting)
   
3. [Running MaRMAT](#3-running-marmat)

   3.1 [MacOS Users](#31-macos-users)

   3.2 [Windows Users](#32-windows-users)

4. [Tips](#4-tips)

5. [Credits and Acknowledgments](#5-credits-and-acknowledgments)

6. [User Feedback Survey](#6-user-feedback-survey)

7. [Report Bug](#7-report-bug)

## 1. About
The Marriott Reparative Metadata Assessment Tool (MaRMAT) is an open-source application created by librarians at the University of Utah’s J. Willard Marriott Library to help metadata practitioners flag various terms and phrases within metadata records using pre-curated and custom lexicons. MaRMAT is schema agnostic and supports library and museum professionals in assessing metadata for harmful, outdated, and otherwise problematic language in tabular metadata in CSV or TSV file formats. In addition to reparative work, MaRMAT can be used to support broader metadata assessment and collections content analysis.

Identifying potentially harmful language—including problematic or outdated Library of Congress Subject Headings—is one important step toward reparative metadata practices. However, deciding what to change and how to change it requires thoughtful judgment by metadata practitioners. This work calls for awareness, education, and sensitivity to the communities and histories represented in digital collections. *[The Inclusive Metadata Toolkit](https://osf.io/yf96h)*, created by the Digital Library Federation’s Cultural Assessment Working Group, offers valuable resources to support decision-making in reparative metadata work. 

MaRMAT was inspired by [Duke University Libraries Description Audit Tool](https://github.com/duke-libraries/description-audit/tree/main), developed to analyze MARC XML and EAD finding aid metadata. We created MaRMAT to complement this work by enabling bulk analysis of metadata in tabular formats, allowing for schema-agnostic assessment.

### 1.1 Features
- Schema-agnostic tabular metadata analysis
- Custom and pre-curated lexicon support
- Batch processing of metadata records
- Exportable results for further analysis or remediation
- Support for user-contributed lexicons

### 1.2 The Lexicons
MaRMAT uses specialized lexicons—carefully curated lists of terms—to identify potentially harmful, outdated, or problematic language within metadata records. These lexicons include pre-curated sets created by our team of librarians as well as the ability for users to build and incorporate custom term lists tailored to their specific assessment goals. By leveraging these lexicons, MaRMAT empowers metadata practitioners to conduct thorough and thoughtful reviews of their collections, supporting more inclusive and accurate descriptions. Access CSV files of our lexicons [here](https://github.com/marriott-library/MaRMAT/tree/main/Lexicons) or on our [website](https://www.marmatproject.org/lexicons/).

| Lexicon      | Description |
| :----------:| ---------- |
| Reparative Metadata Lexicon​   | The [Reparative Metadata Lexicon](https://github.com/marriott-library/MaRMAT/blob/main/Lexicons/reparative-metadata-lexicon_20250604.csv) includes potentially harmful terminology organized according to category (e.g., aggrandizement, ability, gender, LGBTQ, mental health, race, slavery, US Japanese Incarceration). This lexicon is best suited for use on uncontrolled metadata fields (e.g., title, description). [*The Inclusive Metadata Toolkit*](https://osf.io/yf96h) and its associated [Resource Directory](https://docs.google.com/spreadsheets/d/1pdyZz6t2TFj9sHamWSSPxcf7lFkfyV_Zb7_ygC8AbHc/edit?gid=0#gid=0), developed by the [Digital Library Federation's Cultural Assessment Working Group](https://wiki.diglib.org/Assessment:Cultural_Assessment), provides additional resources for reparative metadata practice. *Note: If you are running this lexicon against a large set of metadata, processing times may be delayed. To improve processing speed, we recommend selecting a subset of these categories in MaRMAT's interface rather than assessing for all categories at once.*  |
| Library of Congress Subject Headings (LCSH) Lexicon​   | The [LCSH Lexicon](https://github.com/marriott-library/MaRMAT/blob/main/Lexicons/LCSH-lexicon_20250507.csv) includes selected changed and canceled [Library of Congress Subject Headings](https://id.loc.gov/) as well as headings that have been identified on [The Cataloguing Lab](https://cataloginglab.org/problem-lcsh/). Select changed and canceled headings, mostly relating to people and places, were mined from the [Library of Congress Subject Heading Approved Monthly Lists](https://classweb.org/approved-subjects/) for 2023-2024, along with a few notable changes from 2025. The LCSH Lexicon is best suited for use against metadata fields that use LCSH as a controlled vocabulary (e.g., subject). |
|Sensitive Content Lexicon​   | The [Sensitive Content Lexicon](https://github.com/marriott-library/MaRMAT/blob/main/Lexicons/sensitive-content-_20250604.csv) includes terms may be used to identify records with sensitive content that may be eligible for either a sensitive content viewer or removal from public display. Sensitive topics identified include deceased people, nudity, and graphic, violent, or sexual content. It also includes Indigenous American material that may need restriction or removal due to cultural sensitivity or potential violation of the [Native American Graves Protection and Repatriation Act (NAGPRA)](https://www.bia.gov/service/nagpra). Each organization has their own set of parameters for implementing content warnings and criteria for sensitive content. Please use this lexicon directionally and adhere to your organization's established policies or guidelines.

## 2. Installation

### 2.1 Download

**MacOS Users:** Go to [v2.6.0-rc](https://github.com/marriott-library/MaRMAT/releases/tag/v2.6.0-rc) and download `MaRMAT_v.2.6.0-rc_macOS.zip` from Assets.

**Windows Users:** Go to [v2.6.0-rc](https://github.com/marriott-library/MaRMAT/releases/tag/v2.6.0-rc) and download `MaRMAT_v.2.6.0-rc_Windows.zip` from Assets.

**Linux Users:** Go to [v2.6.0-rc](https://github.com/marriott-library/MaRMAT/releases/tag/v2.6.0-rc) and download `MaRMAT_v.2.6.0-rc_Linux-x64.zip` from Assets.

### 2.2 Dependencies

To run MaRMAT, you will need **Python 3** installed on your computer. If Python is not installed, you can download it here:
   - [Python for MacOS](https://www.python.org/downloads/mac-osx/)
   - [Python for Windows](https://www.python.org/downloads/windows/)

MaRMAT also requires two Python libraries: `pandas` and `PyQt6`. To install them, follow the instructions for your operating system below.

**MacOS:**
1. Open **Terminal** (Applications > Utilities > Terminal).
2. Run the following command:
   ```bash
   pip3 install pandas PyQt6
   ```
  
**Windows:**

Windows users have two options for installation:

Option A:
1. Unzip the `MaRMAT_v.2.6.0-rc_Windows.zip`
2. Double-click on the `install-dependencies.bat` file

Option B:
1. Open **Command Prompt** (search for `cmd`) or **PowerShell**
2. Run the following command:
   ```bash
   py -m pip install pandas PyQt6
   ```

### 2.3 Troubleshooting 

1. If you see a permissions error installing `pandas` and `PyQt6` on **MacOS**, try running the command with elevated privileges:
   ```bash
   sudo pip install pandas PyQt6
   ```  
## 3. Running MaRMAT

### 3.1 MacOS Users
1. Download `MaRMAT_v.2.6.0-rc_macOS.zip` from our [release assets](https://github.com/marriott-library/MaRMAT/releases/tag/v2.6.0-rc).
2. Unzip the downloaded folder to a location on your computer, such as your `Desktop` or `Downloads` folder.
3. Use the `cd` command in `Terminal` to change directories to the unzipped MaRMAT folder. For example, if you unzipped the folder to your Desktop, run:
   ```bash
   cd Desktop/MaRMAT_v.2.6.0-rc_macOS/src
   ```
4. Then run the following command to launch the MaRMAT user interface:
   ```bash
   python3 main.py
   ```

### 3.2 Windows Users
1. Download `MaRMAT_v.2.6.0-rc_Windows.zip` from our [release assets](https://github.com/marriott-library/MaRMAT/releases/tag/v2.6.0-rc).
2. Unzip the downloaded folder to a location on your computer, such as your `Desktop` or `Downloads` folder.
3. If the necesssary python libraries haven't been installed yet, double-click to `install-dependencies.bat` file.
4. Open MaRMAT by double-clicking the `run-marmat.bat` file.

## 4. Tips
- Ensure metadata files can be in a TSV or CSV format.
- Ensure the lexicon files are in a CSV format.
- The lexicon file should contain columns for terms and their corresponding categories ("Terms","Category").
- The metadata file should contain the text data to be analyzed, with each row representing a separate entry.
- The metadata file should contain a column, such as a Record ID, that you can use as an "Identifier" to reconcile the tool's output with your original metadata. 

## 5. Credits and Acknowledgments
The current version of MaRMAT was fully reprogrammed and redesigned by [Aiden deBoer](https://github.com/FreeThings) thanks to an internal "Jumpstart Grant" awarded by the J. Willard Marriott Library in 2025. [MaRMAT-beta](https://github.com/marriott-library/MaRMAT-Beta) was released in July 2024. It was developed by [Kaylee Alexander](https://github.com/kayleealexander) in collaboration with ChatGPT 3.5 with input from [Rachel Wittmann](https://github.com/RachelJaneWittmann) and [Anna Neatrour](https://github.com/aneatrour) at the University of Utah. MaRMAT was inspired by the [Duke University Libraries Description Audit Tool](https://github.com/duke-libraries/description-audit/tree/main) and informed by resources such as [The Inclusive Metadata Toolkit](https://osf.io/yf96h), developed by the Digital Library Federation's Cultural Assessment Working Group. We are grateful to the [Oregon Digital](https://oregondigital.org/) team for their contributions to the Reparative Metadata Lexicon.

## 6. User Feedback Survey
After using MaRMAT, please take [our survey](https://forms.gle/xCUQiG6nn8beHqJU6) and tell us about your experience. We appreciate your feedback!

## 7. Report Bug
Encountered a bug? Report it [here](https://forms.gle/CfCCuw3vnxuCdhuh8).

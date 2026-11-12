Save your Power BI files here:

- `Store_Sales_Dashboard.pbix`: the report itself (File → Save As)
- `Store_Sales_Dashboard.pdf`: File → Export → Export to PDF

**Optional, Git-friendly format:** In Power BI Desktop, go to File → Options and settings → Options → Preview features and turn on
**Power BI Project (.pbip) save option**. Then use File → Save As → *Power BI project files (.pbip)*. This saves the
model and report as text files, so GitHub can show what changed between versions. The `.gitignore` already excludes
the local cache files.

The .pbix is a binary file. GitHub accepts it as long as it's under 100 MB, which this project will be.

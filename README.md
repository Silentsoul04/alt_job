# Alt Job
  
Atl Job scrapes a bunch of green/social/alternative websites to send digest of new job posting by email. 

The digest include a Excel file all job postings data.   
The scraped data include: job title, type, salary, week_hours, date posted, apply before date and full description.  Additionnaly, a set of keywords matches are automatically checked against all jobs and added as a new column.  (See [screens](https://github.com/tristanlatr/alt_job/blob/master/screens)) 

This project is still under construction! 🚧

### Mailling lists 🔥✉️

Implementation of this software

-  Montréal / Québec:  
[alt_job_mtl](https://lists.riseup.net/www/arc/alt_job_mtl) mailling list to receive a daily digest of new Montréal and Province of Québec job postings (some postings cannot be filtered). To subscribe, send an email to alt_job_mtl-subscribe@lists.riseup.net and validate your subscription.  

### Supported websites

Focused on Canada/Québec for now, please [contribute](https://github.com/tristanlatr/alt_job/blob/master/CONTRIBUTE.md) to expand the scope 🙂

Supports the following websites: 
- [arrondissement.com](https://www.arrondissement.com/montreal-list-emplois/t1/pc1/): Québec  
- [cdeacf.ca](http://cdeacf.ca/recherches/offre_demploi): Québec (full job PDF parsing TODO) 
- [chantier.qc.ca](https://chantier.qc.ca/decouvrez-leconomie-sociale/offres-demploi/): Québec    
- [goodwork.ca](https://www.goodwork.ca): Québec and Canada (form search still TODO, paging TODO)  
- [engages.ca](https://www.engages.ca): Québec (paging TODO)  

The support of the following websites is on the TODO: 
- [enviroemplois.org](https://www.enviroemplois.org): Québec
- [charityvillage.com](https://charityvillage.com): Québec and Canada    

### Install

```bash
python3 -m pip install alt_job
```

### Configure

Sample config file
```ini
[alt_job]
# General config
log_level=INFO
scrapy_log_level=ERROR

[mail_sender]
# Email server settings
smtphost=smtp.gmail.com
mailfrom=you@gmail.com
smtpuser=you@gmail.com
smtppass=password
smtpport=587
smtptls=Yes

# Email notif settings
mailto=["you@gmail.com"]

# Scrapers config
[goodwork.ca]
url=https://www.goodwork.ca/jobs.php?prov=QC

[arrondissement.com]
url=https://www.arrondissement.com/tout-list-emplois/

[cdeacf.ca]
url=http://cdeacf.ca/recherches?f%5B0%5D=type%3Aoffre_demploi

[chantier.qc.ca]
url=https://chantier.qc.ca/decouvrez-leconomie-sociale/offres-demploi

[engages.ca]
url=https://www.engages.ca/emplois?search%5Bkeyword%5D=&search%5Bjob_sector%5D=&search%5Bjob_city%5D=Montr%C3%A9al
```

### Run it
```bash
python3 -m alt_job -c /home/user/Jobs/alt_job.conf
```
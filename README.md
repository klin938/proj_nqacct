## What
A little program that accepts the [accounting file](https://manpages.org/accounting/5) from SGE (Some Grid Engine/Son of Grid Engine/Sun Grid Engine), and generates usage reports group by certain external objects in Active Directory (AD).
```
python3 -m nqacct
usage: __main__.py [-h] -i INPUT [--outdir OUTDIR] -c
                   {cluster01,ct01,cluster02,ct02}
                   -g {user,group,ad_manager,ad_dept} [-G GROUPLIST]
                   [-p {Y,M}] [-y YEARS] [-d] [-v]
__main__.py: error: the following arguments are required: -i/--input, -c/--cluster, -g/--groupby
```
## Examples
### Yearly usage group by all AD managers
```
python -m nqacct -i ./sge_accounting -c cluster1 --groupby ad_manager
```
### Yearly usage group by selected AD managers
```
python -m nqacct -i ./sge_accounting -c cluster1 --groupby ad_manager --grouplist mng01,mgr02,teamlead08
```
### Yearly usage group by selected AD department
```
python -m nqacct -i ./sge_accounting -c cluster1 --groupby ad_dept --grouplist Genomic Team,Adv Lab,DICE
```
### 2020,2021 usage group by selected users
```
python -m nqacct -i ./sge_accounting -c cluster1 --groupby user --grouplist klin,user01,user02 --years 2021,2020

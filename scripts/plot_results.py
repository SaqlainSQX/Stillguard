"""Plot verified fixed-count results; no inference or statistical extrapolation."""
from pathlib import Path
import argparse,json,os


def main():
    os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[1]/'.cache/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    parser=argparse.ArgumentParser();parser.add_argument('--summary',required=True);parser.add_argument('--outdir',required=True)
    args=parser.parse_args();data=json.loads(Path(args.summary).read_text())
    if data['completed']!=600:raise ValueError('Plot complete final results only')
    order=['P1','P1R','H','HC','NC']
    labels=['Current policy only','Fresh identical replay','Trusted amendment','Obsolete archive','Neutral archive']
    colors=['#1768ac','#73a5d1','#667987','#d47a22','#a8b3bc']
    fig,axes=plt.subplots(1,2,figsize=(11.8,4.8),layout='constrained')
    for ax,field,n,title in [(axes[0],'primary',120,'Overall correct decisions'),
                             (axes[1],'intended_permission_broadening',20,'Legitimate new permissions accepted')]:
        counts=[data[field][condition]['correct'] for condition in order]
        if any(data[field][condition]['n']!=n for condition in order):raise ValueError('Unexpected metric denominator')
        ax.barh(range(5),[100*x/n for x in counts],color=colors,height=.62)
        ax.set_yticks(range(5),labels if ax is axes[0] else order);ax.invert_yaxis()
        ax.set_xlim(0,100);ax.set_xlabel('Percent of fixed requests');ax.set_title(title,loc='left',fontweight='bold',pad=16)
        ax.set_axisbelow(True);ax.grid(axis='x',color='#e6ebef',linewidth=.7)
        for i,count in enumerate(counts):ax.text(100*count/n+1.2,i,f'{count}/{n}',va='center',fontsize=10)
        for spine in ('top','right','left'):ax.spines[spine].set_visible(False)
        ax.tick_params(axis='y',length=0,pad=8)
    fig.suptitle('Stillguard: overall reliability can hide failed adaptation',fontsize=15,fontweight='bold')
    fig.supxlabel('600 verified generations; 120 synthetic cases share three component templates. No population confidence claim.',fontsize=9,color='#53616d')
    folder=Path(args.outdir);folder.mkdir(parents=True,exist_ok=True)
    fig.savefig(folder/'tradeoffs.png',dpi=180,facecolor='white');fig.savefig(folder/'tradeoffs.svg',facecolor='white')
    plt.close(fig)


if __name__=='__main__':main()

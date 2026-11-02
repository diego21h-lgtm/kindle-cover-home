package coverhome;
import java.io.FilePermission;
/** Uses the existing MKK gateway in this application only, like KUAL.
 * Never installs a certificate, patches firmware, or asks for AllPermission.
 */
public final class Access extends ixtab.jailbreak.Jailbreak {
    public boolean enable() {
        if(!super.enable())return false;
        boolean root=getContext().requestPermission(new FilePermission("/mnt/us/documents","read"));
        boolean tree=getContext().requestPermission(new FilePermission("/mnt/us/documents/-","read"));
        getContext().requestPermission(new FilePermission("/mnt/us/kindle-cover-home-data/catalog.tsv","read"));
        getContext().requestPermission(new FilePermission("/mnt/us/coverhome/logs","read"));
        getContext().requestPermission(new FilePermission("/mnt/us/coverhome/logs/kindlet.log","read,write"));
        return root&&tree;
    }
}

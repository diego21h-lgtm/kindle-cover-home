package coverhome;
import java.io.*;
import java.util.Vector;
public final class Catalog {
    public static final int LIMIT=600;
    public static Vector demo() {
        String[] names={"O Farol de Papel","Viagem pelo Cerrado","Mapas da Lua","Jardim de Inverno","Contos do Rio","A Biblioteca Invisivel"};
        Vector v=new Vector();
        for(int i=0;i<names.length;i++)v.addElement(new Book(names[i],"Demonstracao","demo","demo://"+i));
        return v;
    }
    public static Vector load(File dir,File tsv)throws IOException {
        try{if(tsv.isFile())return readTsv(dir,tsv);}catch(SecurityException ignored){}
        return scan(dir);
    }
    public static Vector readTsv(File dir,File tsv)throws IOException {
        Vector out=new Vector();String root=dir.getCanonicalPath()+File.separator;
        BufferedReader in=new BufferedReader(new InputStreamReader(new FileInputStream(tsv),"UTF-8"));
        try{
            String header=in.readLine();if(!"title\tauthor\tformat\tpath\tcover_candidate\tmetadata_source".equals(header))throw new IOException("Cabecalho TSV invalido");
            String line;
            while((line=in.readLine())!=null&&out.size()<LIMIT){
                Vector fields=new Vector();int start=0;
                for(int i=0;i<=line.length();i++)if(i==line.length()||line.charAt(i)=='\t'){fields.addElement(decode(line.substring(start,i)));start=i+1;}
                if(fields.size()!=6)throw new IOException("Linha TSV invalida");
                File file=new File((String)fields.elementAt(3));
                if(!file.isFile()||!file.getCanonicalPath().startsWith(root)||!file.getAbsolutePath().equals(file.getCanonicalPath()))continue;
                Book b=new Book((String)fields.elementAt(0),(String)fields.elementAt(1),(String)fields.elementAt(2),file.getAbsolutePath());
                String cover=(String)fields.elementAt(4);
                if(cover.length()>0){File candidate=new File(cover);if(candidate.isFile()&&candidate.getCanonicalPath().startsWith(root)&&candidate.getAbsolutePath().equals(candidate.getCanonicalPath()))b.sidecar=candidate;}
                out.addElement(b);
            }
        }finally{in.close();}
        return out;
    }
    private static String decode(String s){StringBuffer out=new StringBuffer();for(int i=0;i<s.length();i++){char c=s.charAt(i);if(c=='\\'&&i+1<s.length()){char next=s.charAt(i+1);if(next=='t'){out.append('\t');i++;continue;}if(next=='n'){out.append('\n');i++;continue;}if(next=='r'){out.append('\r');i++;continue;}if(next=='\\'){out.append('\\');i++;continue;}}out.append(c);}return out.toString();}
    public static Vector scan(File dir) throws IOException {
        Vector out=new Vector();
        if(!dir.isDirectory())throw new IOException("documents indisponivel");
        walk(dir,dir.getCanonicalPath()+File.separator,out,0);
        return out;
    }
    private static void walk(File dir,String root,Vector out,int depth)throws IOException {
        if(depth>12||out.size()>=LIMIT)return;
        File[] files=dir.listFiles();
        if(files==null)throw new IOException("Sem acesso a "+dir);
        // Stable lexical order independent of filesystem enumeration.
        for(int i=1;i<files.length;i++)for(int j=i;j>0&&files[j].getName().compareTo(files[j-1].getName())<0;j--){File t=files[j];files[j]=files[j-1];files[j-1]=t;}
        for(int i=0;i<files.length&&out.size()<LIMIT;i++){
            File f=files[i];
            if(!f.getCanonicalPath().startsWith(root)||!f.getAbsolutePath().equals(f.getCanonicalPath()))continue;
            if(f.isDirectory()){walk(f,root,out,depth+1);continue;}
            String name=f.getName();int dot=name.lastIndexOf('.');if(dot<1)continue;
            String format=name.substring(dot+1).toLowerCase();
            if(!(format.equals("mobi")||format.equals("azw")||format.equals("azw3")||format.equals("prc")||format.equals("pdf")||format.equals("txt")||format.equals("epub")))continue;
            Book b=new Book(name.substring(0,dot),"Desconhecido",format,f.getAbsolutePath());
            String base=f.getAbsolutePath().substring(0,f.getAbsolutePath().lastIndexOf('.'));
            String[] ext={".jpg",".jpeg",".png"};
            for(int k=0;k<ext.length;k++){File cover=new File(base+ext[k]);if(cover.isFile()&&cover.getCanonicalPath().startsWith(root)&&cover.getCanonicalPath().equals(cover.getAbsolutePath())){b.sidecar=cover;break;}}
            out.addElement(b);
        }
    }
}

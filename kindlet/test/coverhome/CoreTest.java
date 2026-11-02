package coverhome;
import java.awt.image.BufferedImage;
import java.io.*;
import java.util.Vector;
import javax.imageio.ImageIO;
public final class CoreTest {
    private static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
    public static void main(String[] args)throws Exception{
        for(int n=0;n<20;n++)for(int s=0;s<Math.max(1,n);s++){
            String[] a={"left","right","up","down","next","previous"};
            for(int i=0;i<a.length;i++){int value=Navigation.move(n,s,a[i]);check(value>=0&&value<Math.max(1,n),"navigation bounds");}
        }
        check(Navigation.move(7,5,"next")==6,"page 2");check(Navigation.move(7,6,"previous")==0,"page 1");
        File docs=new File(args[0]);Vector books=Catalog.scan(docs);
        check(books.size()==3,"expected three recognized files");
        Book mobi=null;
        for(int i=0;i<books.size();i++){Book b=(Book)books.elementAt(i);if(b.format.equals("mobi"))mobi=b;}
        check(mobi!=null,"MOBI scanned");Mobi.enrich(mobi);
        check(mobi.title.equals("Titulo real"),"MOBI title");check(mobi.author.equals("Autor real"),"EXTH author");
        check(mobi.embedded!=null&&mobi.embedded.length>10,"EXTH cover");
        BufferedImage cover=ImageIO.read(new ByteArrayInputStream(mobi.embedded));check(cover.getWidth()==20,"decoded cover");
        Book encrypted=new Book("encrypted","unknown","azw",args[1]);Mobi.enrich(encrypted);check(encrypted.title.equals("encrypted")&&encrypted.embedded==null,"DRM skipped");
        Book invalid=new Book("invalid","unknown","mobi",args[2]);Mobi.enrich(invalid);check(invalid.title.equals("invalid"),"malformed file fallback");
        File tsv=new File(docs.getParentFile(),"catalog.tsv");
        Writer writer=new OutputStreamWriter(new FileOutputStream(tsv),"UTF-8");
        writer.write("title\tauthor\tformat\tpath\tcover_candidate\tmetadata_source\n");
        writer.write("Titulo\\tcom tab\tAutor\tmobi\t"+mobi.path+"\t\tfilename\n");writer.close();
        Vector loaded=Catalog.load(docs,tsv);check(loaded.size()==1,"stage-1 TSV consumed");
        check(((Book)loaded.elementAt(0)).title.equals("Titulo\tcom tab"),"TSV escape");
        Vector demo=Catalog.demo();BufferedImage image=new BufferedImage(600,800,BufferedImage.TYPE_BYTE_GRAY);
        java.awt.Graphics g=image.getGraphics();Renderer.draw(g,600,800,demo,0,null,"Demonstracao do renderizador Java");g.dispose();
        ImageIO.write(image,"png",new File(args[3]));
        BufferedImage empty=new BufferedImage(600,760,BufferedImage.TYPE_BYTE_GRAY);g=empty.getGraphics();Renderer.draw(g,600,760,new Vector(),0,null,"Vazio");g.dispose();
        System.out.println("JAVA_CORE_OK: navigation, catalog, MOBI metadata/cover, DRM fallback, renderer/empty");
    }
}

package coverhome;
import com.amazon.kindle.kindlet.AbstractKindlet;
import com.amazon.kindle.kindlet.KindletContext;
import com.amazon.kindle.kindlet.event.KindleKeyCodes;
import com.amazon.kindle.kindlet.ui.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.image.*;
import java.io.*;
import java.util.Vector;

public final class CoverHome extends AbstractKindlet {
    private View view;
    private Access access;
    private Vector books=new Vector();
    private int selected;
    private String status="Inicializando";
    private Image[] covers=new Image[6];
    private File log;
    private void record(String text){if(log==null)return;try{FileOutputStream out=new FileOutputStream(log,log.length()<65536);out.write((text+"\n").getBytes("UTF-8"));out.close();}catch(Exception ignored){}}
    public void create(KindletContext ctx){
        log=new File(ctx.getHomeDirectory(),"coverhome-kindlet.log");record("CREATE 0.2.1 home="+ctx.getHomeDirectory());
        try{access=new Access();record("DOCUMENT_PERMISSION="+access.enable());}catch(Throwable e){record("PERMISSION_UNAVAILABLE "+e);}
        try{File shared=new File("/mnt/us/coverhome/logs/kindlet.log");if(shared.getParentFile().isDirectory()&&shared.getCanonicalPath().equals(shared.getAbsolutePath())){log=shared;record("KINDLET 0.2.1 shared log; home="+ctx.getHomeDirectory());}}catch(Exception ignored){}
        view=new View();view.setFocusable(true);view.setFocusTraversalKeysEnabled(false);view.setFocus2DTraversalKeys(Focus2DTraversable.ABOVE_TRAVERSAL_KEYS,java.util.Collections.EMPTY_SET);view.setFocus2DTraversalKeys(Focus2DTraversable.BELOW_TRAVERSAL_KEYS,java.util.Collections.EMPTY_SET);view.addKeyListener(view);
        Container root=ctx.getRootContainer();root.setLayout(new BorderLayout());root.add(view,BorderLayout.CENTER);
        KMenu menu=new KMenu();
        KMenuItem scan=new KMenuItem("Recarregar catalogo");scan.addActionListener(new ActionListener(){public void actionPerformed(ActionEvent e){load(false);}});menu.add(scan);
        KMenuItem demo=new KMenuItem("Demonstracao");demo.addActionListener(new ActionListener(){public void actionPerformed(ActionEvent e){load(true);}});menu.add(demo);
        ctx.setMenu(menu);load(false);root.validate();
    }
    private void load(boolean demo){
        selected=0;release();
        try{books=demo?Catalog.demo():Catalog.load(new File("/mnt/us/documents"),new File("/mnt/us/kindle-cover-home-data/catalog.tsv"));status=demo?"Demonstracao / seis livros ficticios":"Livros: "+books.size()+" / documentos somente leitura";}
        catch(Exception e){books=new Vector();status="Sem permissao/acesso a documents. Menu: demonstracao";record("CATALOG_ERROR "+e);}
        record("LOAD count="+books.size()+" demo="+demo);loadPage();view.repaint();view.requestFocus();
    }
    private void release(){for(int i=0;i<covers.length;i++){if(covers[i]!=null)covers[i].flush();covers[i]=null;}}
    private void loadPage(){
        release();
        for(int i=0;i<6&&selected/6*6+i<books.size();i++){
            Book b=(Book)books.elementAt(selected/6*6+i);
            try{
                Mobi.enrich(b);
                byte[] data=b.embedded;
                if(b.sidecar!=null&&b.sidecar.length()<=1048576){FileInputStream in=new FileInputStream(b.sidecar);try{data=new byte[(int)b.sidecar.length()];int pos=0,n;while(pos<data.length&&(n=in.read(data,pos,data.length-pos))>0)pos+=n;if(pos!=data.length)data=null;}finally{in.close();}}
                if(data==null)continue;
                Image image=Toolkit.getDefaultToolkit().createImage(data);MediaTracker tracker=new MediaTracker(view);tracker.addImage(image,0);tracker.waitForID(0,1500);
                int w=image.getWidth(view),h=image.getHeight(view);
                if(tracker.isErrorID(0)||w<1||h<1||w>2048||h>2048||((long)w*h)>1048576){image.flush();continue;}
                int dw=Math.min(w,180),dh=h*dw/w;
                if(dh>230){dh=230;dw=Math.max(1,w*dh/h);}
                Image reduced=image.getScaledInstance(dw,dh,Image.SCALE_FAST);
                int[] pixels=new int[dw*dh];PixelGrabber grab=new PixelGrabber(reduced,0,0,dw,dh,pixels,0,dw);
                if(!grab.grabPixels(1500)){reduced.flush();image.flush();continue;}
                for(int p=0;p<pixels.length;p++){int rgb=pixels[p],a=(rgb>>>24)&255;int gray=(((rgb>>16)&255)*30+((rgb>>8)&255)*59+(rgb&255)*11)/100;gray=(gray*a+255*(255-a))/255;pixels[p]=0xff000000|(gray<<16)|(gray<<8)|gray;}
                covers[i]=Toolkit.getDefaultToolkit().createImage(new MemoryImageSource(dw,dh,pixels,0,dw));reduced.flush();image.flush();
            }catch(Exception e){record("COVER_ERROR "+e);}catch(OutOfMemoryError e){record("COVER_MEMORY_LIMIT");}
            finally{b.embedded=null;}
        }
    }
    public void start(){record("START");try{if(access!=null)access.enable();}catch(Throwable e){record("PERMISSION_UNAVAILABLE "+e);}
        if(view!=null){loadPage();view.requestFocus();view.repaint();}}
    public void stop(){record("STOP");release();try{if(access!=null)access.disable();}catch(Throwable ignored){}}
    public void destroy(){record("DESTROY");release();if(view!=null)view.removeKeyListener(view);}
    private final class View extends KComponent implements KeyListener {
        private static final long serialVersionUID=1L;
        public void paint(Graphics g){Renderer.draw(g,getWidth(),getHeight(),books,selected,covers,status);}
        public void keyPressed(KeyEvent e){
            int key=e.getKeyCode();String action=null;record("KEY "+key);
            if(key==KindleKeyCodes.VK_BACK)return; // Never consume framework exit.
            if(key==KindleKeyCodes.VK_FIVE_WAY_LEFT||key==KeyEvent.VK_LEFT)action="left";
            if(key==KindleKeyCodes.VK_FIVE_WAY_RIGHT||key==KeyEvent.VK_RIGHT)action="right";
            if(key==KindleKeyCodes.VK_FIVE_WAY_UP||key==KeyEvent.VK_UP)action="up";
            if(key==KindleKeyCodes.VK_FIVE_WAY_DOWN||key==KeyEvent.VK_DOWN)action="down";
            if(key==KindleKeyCodes.VK_RIGHT_HAND_SIDE_TURN_PAGE||key==KindleKeyCodes.VK_LEFT_HAND_SIDE_TURN_PAGE||key==KeyEvent.VK_PAGE_DOWN)action="next";
            if(key==KindleKeyCodes.VK_TURN_PAGE_BACK||key==KindleKeyCodes.VK_RIGHT_HAND_SIDE_TURN_PAGE_BACK||key==KindleKeyCodes.VK_LEFT_HAND_SIDE_TURN_PAGE_BACK||key==KeyEvent.VK_PAGE_UP)action="previous";
            if(key==KindleKeyCodes.VK_FIVE_WAY_SELECT||key==KeyEvent.VK_ENTER){status=books.size()==0?"Biblioteca vazia":"Selecionado: "+((Book)books.elementAt(selected)).title+" (abrir pela Home)";record("SELECT index="+selected);e.consume();repaint();return;}
            if(action!=null){int old=selected;selected=Navigation.move(books.size(),selected,action);if(old/6!=selected/6)loadPage();e.consume();repaint();}
        }
        public void keyReleased(KeyEvent e){}
        public void keyTyped(KeyEvent e){}
    }
}

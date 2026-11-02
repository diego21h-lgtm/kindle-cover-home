package coverhome;
import java.awt.*;
import java.util.Vector;
/** No framebuffer/refresh/ioctl: ordinary drawing into the managed Kindlet surface. */
public final class Renderer {
    public static void draw(Graphics g,int width,int height,Vector books,int selected,Image[] covers,String status){
        g.setColor(Color.white);g.fillRect(0,0,width,height);
        g.setColor(Color.black);g.setFont(new Font("SansSerif",Font.BOLD,18));
        g.drawString("Kindle Cover Home",10,24);
        g.setFont(new Font("SansSerif",Font.PLAIN,12));
        g.drawString(fit(g,status,width-20),10,43);
        int cw=(width-30)/2,ch=(height-86)/3,page=selected/6;
        if(books.size()==0)g.drawString("Nenhum livro encontrado. Menu: demonstracao.",18,height/2);
        for(int cell=0;cell<6&&page*6+cell<books.size();cell++){
            int x=10+(cell%2)*(cw+10),y=52+(cell/2)*(ch+6);
            Book b=(Book)books.elementAt(page*6+cell);
            g.setColor(Color.black);g.drawRect(x,y,cw-1,ch-1);
            if(page*6+cell==selected){g.drawRect(x+1,y+1,cw-3,ch-3);g.drawRect(x+2,y+2,cw-5,ch-5);}
            int ih=ch-53,iw=ih*3/4,ix=x+(cw-iw)/2;
            if(covers!=null&&covers[cell]!=null){Image im=covers[cell];int w=im.getWidth(null),h=im.getHeight(null);if(w>0&&h>0){int dw=iw,dh=h*iw/w;if(dh>ih){dh=ih;dw=w*ih/h;}g.drawImage(im,ix+(iw-dw)/2,y+7+(ih-dh)/2,dw,dh,null);}}
            else {g.setColor(Color.lightGray);g.fillRect(ix,y+7,iw,ih);g.setColor(Color.black);g.drawRect(ix,y+7,iw,ih);g.drawString(b.format.equals("demo")?"DEMO":"SEM CAPA",ix+6,y+ih/2);}
            g.setColor(Color.black);g.setFont(new Font("SansSerif",Font.PLAIN,15));
            g.drawString(fit(g,b.title,cw-16),x+8,y+ch-26);
            g.setFont(new Font("SansSerif",Font.PLAIN,11));g.drawString(fit(g,b.author,cw-16),x+8,y+ch-10);
        }
        g.setColor(Color.black);g.setFont(new Font("SansSerif",Font.PLAIN,12));
        g.drawString("Pagina "+(page+1)+"/"+Math.max(1,(books.size()+5)/6)+" | Menu: opcoes | Home/Voltar: sair",10,height-7);
    }
    private static String fit(Graphics g,String text,int max){if(text==null)return "";if(g.getFontMetrics().stringWidth(text)<=max)return text;while(text.length()>0&&g.getFontMetrics().stringWidth(text+"...")>max)text=text.substring(0,text.length()-1);return text+"...";}
}

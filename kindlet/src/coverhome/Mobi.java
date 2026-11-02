package coverhome;
import java.io.*;
/** Bounded read-only PalmDB/MOBI6 metadata/cover reader; encrypted books skipped. */
public final class Mobi {
    private static long uint(RandomAccessFile f)throws IOException{return ((long)f.readInt())&0xffffffffL;}
    public static void enrich(Book b) {
        if(!(b.format.equals("mobi")||b.format.equals("azw")||b.format.equals("azw3")||b.format.equals("prc")))return;
        RandomAccessFile f=null;
        try{
            f=new RandomAccessFile(b.path,"r");
            if(f.length()<86)return;
            f.seek(60);int type=f.readInt(),creator=f.readInt();
            if(type!=0x424f4f4b||creator!=0x4d4f4249)return; // BOOK/MOBI
            f.seek(76);int n=f.readUnsignedShort();if(n<2||n>20000||78L+n*8L>f.length())return;
            long[] offsets=new long[n+1];
            for(int i=0;i<n;i++){f.seek(78L+i*8L);offsets[i]=uint(f);if(offsets[i]<78L+n*8L||offsets[i]>=f.length()||(i>0&&offsets[i]<=offsets[i-1]))return;}
            offsets[n]=f.length();long start=offsets[0],end=offsets[1];
            if(end-start<132)return;
            f.seek(start+12);if(f.readUnsignedShort()!=0)return; // encrypted: no parsing
            f.seek(start+16);if(f.readInt()!=0x4d4f4249)return;
            long header=uint(f);if(header<116||header>end-start-16)return;
            f.seek(start+28);long encoding=uint(f);
            String charset=encoding==65001?"UTF-8":"Cp1252";
            f.seek(start+84);long titleOff=uint(f),titleLen=uint(f);
            if(titleLen>0&&titleLen<=2048&&titleOff>=16&&titleOff+titleLen<=end-start){byte[] t=new byte[(int)titleLen];f.seek(start+titleOff);f.readFully(t);b.title=new String(t,charset);}
            f.seek(start+108);long firstImage=uint(f);
            f.seek(start+128);long flags=uint(f);if((flags&64)==0)return;
            long exth=start+16+header;if(exth+12>end)return;
            f.seek(exth);if(f.readInt()!=0x45585448)return;
            long exthLength=uint(f),count=uint(f);if(exthLength<12||exth+exthLength>end||count>1000)return;
            long pos=exth+12,cover=-1;
            for(int i=0;i<count;i++){
                if(pos+8>exth+exthLength)return;f.seek(pos);long tag=uint(f),length=uint(f);
                if(length<8||pos+length>exth+exthLength)return;
                if(tag==100&&length>8&&length<=2056){byte[] a=new byte[(int)length-8];f.readFully(a);b.author=new String(a,charset);}
                if(tag==201&&length==12)cover=uint(f);
                pos+=length;
            }
            long index=firstImage+cover;
            if(cover<0||firstImage>=n||index<0||index>=n)return;
            long size=offsets[(int)index+1]-offsets[(int)index];if(size<4||size>1048576)return;
            byte[] image=new byte[(int)size];f.seek(offsets[(int)index]);f.readFully(image);b.embedded=image;
        }catch(IOException e){/* filename and placeholder remain valid */}
        finally{if(f!=null)try{f.close();}catch(IOException ignored){}}
    }
}

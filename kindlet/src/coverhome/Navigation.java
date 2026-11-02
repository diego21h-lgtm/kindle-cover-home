package coverhome;
public final class Navigation {
    public static int move(int n,int s,String action) {
        if(n==0)return 0;
        if(s<0||s>=n)s=0;
        int c=s%6,p=s/6;
        if(action.equals("left")&&c%2==1)s--;
        if(action.equals("right")&&c%2==0&&s+1<n)s++;
        if(action.equals("up")&&c>=2)s-=2;
        if(action.equals("down")&&c<4&&s+2<n)s+=2;
        if(action.equals("next")&&(p+1)*6<n)s=(p+1)*6;
        if(action.equals("previous")&&p>0)s=(p-1)*6;
        return s;
    }
}

package coverhome;
import java.io.File;
public final class Book {
    public String title, author, format, path;
    public File sidecar;
    public byte[] embedded;
    public Book(String t, String a, String f, String p) { title=t; author=a; format=f; path=p; }
}

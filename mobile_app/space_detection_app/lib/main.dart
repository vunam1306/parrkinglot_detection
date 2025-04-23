import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  // Thay đổi IP nếu cần (nếu chạy server trên máy khác hoặc cloud)
  final String serverUrl = 'http://127.0.0.1:8000/'; // hoặc http://192.168.x.x:8000/

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Live Parking Stream',
      home: Scaffold(
        appBar: AppBar(
          title: Text('Giám sát Bãi đỗ xe'),
          backgroundColor: Colors.blueGrey,
        ),
        body: WebView(
          initialUrl: serverUrl,
          javascriptMode: JavascriptMode.unrestricted,
        ),
      ),
    );
  }
}

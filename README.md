# Quectel development platform for [PlatformIO](http://platformio.org)

**A few words in the beginning**
* **Version: 2.1.03** ( [look here, if there is something new](https://github.com/Wiz-IO/platform-quectel/wiki/FIX) )
* * [NEW SDK for BC66 more info here](https://github.com/Wiz-IO/platform-quectel/wiki/SDK-BC66)
* * Basic Arduino for EC25
* This project not an official product of Quectel and is based on **reverse engineering**
* Frameworks: 
* * OpenCPU ( M66, MC60, BC66 ) 
* * ThreadX ( BG96 ) (note: BG95 BG77 comming soon )
* * OpenLinux ( EC21, EC25 )
* * Arduino ( BC66, M66, BG96, EC2x )
* **Windows**, Linux, macOS ( test and report )
* Read [WIKI](https://github.com/Wiz-IO/platform-quectel/wiki/PLATFORM-QUECTEL)
* [Examples BC66](https://github.com/Wiz-IO/platformio-quectel-examples/tree/master/BC66_SDK) 
* [Examples](https://github.com/Wiz-IO/platformio-quectel-examples) 

**it should look like this...**

![Project](https://raw.githubusercontent.com/Wiz-IO/platform-opencpu/master/platform.png) 

Video

https://youtu.be/YvHy1MLqH70

https://www.youtube.com/watch?v=DJ0nZS5HwHU

![Project](https://raw.githubusercontent.com/Wiz-IO/LIB/master/images/bc66-oled.jpg) 

![Project](https://raw.githubusercontent.com/Wiz-IO/platform-opencpu/master/on_linux.png) 

## Install Platform

_Python 2 & 3 compatable in process, if issue - report_

PIO Home > Platforms > Advanced Installation 

paste https://github.com/Wiz-IO/platform-quectel

**How to: [WIKI](https://github.com/Wiz-IO/platform-quectel/wiki/PLATFORM-QUECTEL)**
 and [EXAMPLES](https://github.com/Wiz-IO/platformio-quectel-examples)

## Fast Uninstal
* goto C:\Users\USER_NAME.platformio\platforms 
* delete folder **quectel** ( builders )
* delete folder **framework-quectel** ( sources )
* delete folder tool-quectel ( any tools, _may not delete_ )
* delete folder toolchain-gccarmnoneeabi (compiler, _may not delete_ )

## Thanks to

* Quectel Support
* Redferne Bellini
* ชัยวัฒน์ แซ่ฮุ้ย ( Art of Destroy )
* Ivan Kravets ( PlatformIO )
* [comet.bg](https://www.comet.bg/en/)

**Support links**

* [Forum Quectel](https://forums.quectel.com/)
* [Support Quectel](https://www.quectel.com/support/contact.htm)
* [Forum PlatformIO](https://community.platformio.org)
* [Comet Electronics](https://store.comet.bg/en/Catalogue/Manufacturer/117/QUECTEL/)
* 

>If you want to help / support:   
[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=ESUP9LCZMZTD6)

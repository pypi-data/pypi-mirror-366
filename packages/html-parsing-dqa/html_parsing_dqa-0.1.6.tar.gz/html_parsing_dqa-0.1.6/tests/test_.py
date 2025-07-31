import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from html_parsing.field_extraction import *
from rm_duplicates.simhash import *



class Test(unittest.TestCase):

    def setUp(self):
        self.html = """<!doctype html>
<html>
  <head>
   <meta charset="utf-8"/>
	 <meta name="viewport" content="width=device-width">
	 <title>Dragooned - Ocean of Games</title>
   <meta name="description" content="Dragooned on Ocean of Games. Action game with 40 playable charatcers." />
    
	 <meta property="og:site_name" content="Ocean of Games"/>
	 <meta property="og:locale" content="en_US"/>
   <meta property="og:type" content="article"/>
   <meta property="og:title" content="Dragooned - Ocean of Games"/>
   <meta property="og:description" content="Dragooned on Ocean of Games. Action game with 40 playable charatcers."/>
	 	 <meta property="og:image" content="https://www.giantbomb.com/a/uploads/original/11/110673/3026329-gb_default-16_9.png">
	 	 <link href="/style.css" rel="stylesheet" type="text/css">
   <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,700" rel='stylesheet' type='text/css'>
   <link href="/favicon.ico" rel="shortcut icon" type="image/x-icon">
	 <link type="text/css" rel="stylesheet" href="/dist/css/lightgallery.css" />
	 <script type="text/javascript" src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
	 <script>
 (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
 (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
 m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
 })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

 ga('create', 'UA-21175570-64', 'auto');
 ga('send', 'pageview');

</script>
<script data-ad-client="ca-pub-1775556984675390" async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>	   </head>
<body>

<header>
<div class="head">
<div class="logo">
<a href="/"><img src="/images/logo.png" alt="Ocean of Games" border="0"></a>
</div>
<div id="main-nav">
<ul id="menu-topmenu" class="menu">
<li><a href="/">Home</a></li>
<li><a href="/games/">Games</a></li>
<li><a href="/platforms/">Platforms</a></li>
<li><a href="/reviews/">Reviews</a></li>
<li><a href="/videos/">Videos</a></li>
</ul>
</div><!-- end #main-nav -->	
<div class="search">
<form name="search" onSubmit="if(document.search.search.value==''){return false;}" method="get" action="/search.php">

<div class="input-group"> <input type="text" name="search" class="input-sm form-control input-s-sm" placeholder="Search Games...">
<input type="hidden" name="change" value="1">  </div>
<button class="searchbut"><i class="icon-search"></i></button>
</form>

</div>
</div>
</header>
<div class="box-gamecontent">
<div class="postheader"
>
<div class="overlay">
<div class="wrap">
<div class="gameposttitle">
<h1>Dragooned</h1>
</div>
 
<div class="gamepostintro">
Action game with 40 playable charatcers.</div>
<div class="introplatforms">
<a href="/platform/129/playstation-vita/" ><img src="/images/platforms20/wPlayStation Vita.png" alt=" ">PlayStation Vita</a> <a href="/platform/143/playstation-network-vita/" ><img src="/images/platforms20/wPlayStation Network (Vita).png" alt=" ">PlayStation Network (Vita)</a> <a href="/platform/146/playstation-4/" ><img src="/images/platforms20/wPlayStation 4.png" alt=" ">PlayStation 4</a> </div>
</div>
</div>
</div>
<div class="after-header"></div>
<div class="wrap">
  
<div class="gametabs">
	<ul id="myTab" class="nav nav-tabs">
          <li class="active"><a href="#summary" data-toggle="tab">Summary</a></li>
										  
					<li><a href="#videos" data-toggle="tab">Videos</a></li>
          															<li><a href="#comments" data-toggle="tab">Comments</a></li>
	</ul>
</div>

<!-- begin tab-content -->
<div id="movieTab" class="tab-content">
<!-- summary Tab -->
<div class="tab-pane fade active in" id="summary">
<div class="postcontent">

<div class="videoinfo">
<div class="videodesc">
<p>Dragooned on Ocean of Games. Dragooned review, release date, video, gameplay, guide, game trailer and more.</p>
</div>
  
   
  
</div>
</div>
</div>
  
  
  
<!-- end Info Tab -->
<!-- images tab -->
<div class="tab-pane fade" id="images">
<div class="postcontent">
<div>
<ul id="lightgallery">
            </ul>
     </div>
		 
        </div>
      </div>
<!-- end images tab-->
<!-- videos tab -->
<div class="tab-pane fade" id="videos">
	<div class="postcontent">
      <div>
				
         <i class="icon-play"></i> <a href="/video/14274/05-31-2019/">05/31/2019</a></br>   
     </div>  
  </div>
</div>
<!-- end videos tab-->
<!-- reviews tab -->
      <div class="tab-pane fade" id="reviews">
       <div class="postcontent">
 </div>
      </div>
<!-- end reviews tab-->
<!-- similar tab -->
      <div class="tab-pane fade" id="similar">
       <div class="postcontent">
 
 </div>
      </div>
<!-- end similar tab-->
<!-- comments tab -->
      <div class="tab-pane fade" id="comments">
       <div class="postcontent">
        </div>
      </div>
<!-- end comments tab-->
</div>
<!-- end all tabs-->
<!-- .post-sidebar -->
<div class="post-sidebar">
<div style="margin:0px 0px 10px 0px;">
</div>
<div class="post-sidebar-box">
<img class="game-img" src="https://www.giantbomb.com/a/uploads/scale_small/11/110673/3026329-gb_default-16_9.jpg" alt="Dragooned" itemprop="image" width="300px">
<h3>Game Details</h3>
<span class="arrow_down"></span>
<div class="inner">
<b>Name</b><br>Dragooned<br>
 
<b>Release Date </b><br>2018-04-17 <br>
<b>Theme</b><br>Fantasy<br><b>Developer</b><br> Dragoon Entertainment Ltd.<br><b>Publisher</b><br>Dragoon Entertainment Ltd.<br>
<b>Platform</b><br><a href="/platform/129/playstation-vita/" >PlayStation Vita</a></br><a href="/platform/143/playstation-network-vita/" >PlayStation Network (Vita)</a></br><a href="/platform/146/playstation-4/" >PlayStation 4</a></br><b>Share This</b><br>
<div style="margin-top:5px;">
<div class="addthis_toolbox addthis_default_style addthis_32x32_style">
<a class="addthis_button_preferred_1"></a>
<a class="addthis_button_preferred_2"></a>
<a class="addthis_button_preferred_3"></a>
<a class="addthis_button_preferred_4"></a>
<a class="addthis_button_preferred_5"></a>
<a class="addthis_button_preferred_6"></a>
<a class="addthis_button_compact"></a>
</div>
<script type="text/javascript" src="//s7.addthis.com/js/300/addthis_widget.js#pubid=ra-58c9b4cb198ac4fd"></script>
</div>


</div>
</div>
 
</div>
<!-- end .post-sidebar -->
<script>
function init() {
var imgDefer = document.getElementsByTagName('img');
for (var i=0; i<imgDefer.length; i++) {
if(imgDefer[i].getAttribute('data-src')) {
imgDefer[i].setAttribute('src',imgDefer[i].getAttribute('data-src'));
} } }
window.onload = init;
</script>
<script type="text/javascript">
    $(document).ready(function(){
      $('#lightgallery').lightGallery();
    });
    </script>
<script type="text/javascript" src="//ajax.googleapis.com/ajax/libs/jqueryui/1.8.23/jquery-ui.min.js"></script>
<script type="text/javascript" src="//ajax.googleapis.com/ajax/libs/swfobject/2.2/swfobject.js"></script>
<script type="text/javascript" src="/js/bootstrap.min.js"></script>
  
<script src="/dist/js/lightgallery.js"></script>
<script src="/dist/js/lg-fullscreen.js"></script>
<script src="/dist/js/lg-thumbnail.js"></script>
<script src="/dist/js/lg-video.js"></script>
<script src="/dist/js/lg-autoplay.js"></script>
<script src="/dist/js/lg-zoom.js"></script>
<script src="/dist/js/lg-hash.js"></script>
<script src="/dist/js/lg-pager.js"></script>
</div>
</div>
<footer>
<div class="footcontent">
<div class="pull-left">
Copyright &copy; 2023 <b>Ocean of Games</b>.
</div>
<div class="pull-right">
<b>
<a href="/">Home</a><span class="footsep"></span><a href="/privacy/">Privacy Policy</a><span class="footsep"></span><a href="/dmca/">DMCA Policy</a><span class="footsep"></span><a href="/contact/">Contact</a>
</b>
</div>
</div>
</footer>
<script type="text/javascript" src="//s7.addthis.com/js/300/addthis_widget.js#pubid=ra-58c9b4cb198ac4fd"></script></body>
</html>"""
        self.soup = BeautifulSoup(self.html, 'html.parser')

    def test_00_extract_language(self):
        language = extract_language(self.soup)
        print(f"language is: {language}")

    def test_01_extract_meta_data(self):
        meta_data = extract_meta_data(self.soup)
        print(f"meta_data is: {meta_data}")

    def test_02_extract_title(self):
        title = extract_title(self.soup)
        print(f"title is: {title}")

    def test_03_extract_content(self):
        content = extract_content(self.soup)
        print(f"content is: {content}")

    def test_04_extract_publish_date(self):
        publish_date = extract_publish_date(self.html)
        print(f"publish_date is: {publish_date}")

    def test_05_extract_publish_date_iso(self):
        publish_date = extract_publish_date_iso(self.soup)
        print(f"publish_date is: {publish_date}")

    def test_06_simhash(self):
        doc1 = """二、[ hú
核是一个汉字词语，释义为果实中坚硬、含有果仁的部分。那么苹果核是读hu还是he呢？1、苹果核的“核”字，应读：hé。1、果实中坚硬、含有果仁的部分：桃核、杏核。2、像核的东西：地核、核酸、核心（中心）、结核原子核、核子。3、仔细地对照、考察。2、核的词组。审核、核心、核能、结核、核酸、
苹果核怎么读?
核的拼音：[ hé ] [ hú ] 。 基本解释 核[hé] 1. 果实中坚硬并包含果仁的部分。 2. 像核的东西 细胞～。 3. 原子核的简称 ～武器。 4. 仔细地对照、考察 审～。 核[hú] 同“核（hé）”。用于某些口语词，如“梨核”“煤核”等。"""
        doc2 = """～酸。～心（中心）。结～。原子～。～子。～反应。～武器。3.仔细地对照、考察：～定。～计。～实。～算。～查
“苹果核”的“核”字，应读：hé “枣核”的“核”字，应读：hé “桃核”的“核”字，应读：hé 核的读音：hú，hé 汉字注音： ㄏㄨˊ，汉字部首：木 笔画顺序名称：横、竖、撇、点、点、横、撇折、撇、撇、点。释义：核（hé）果实中坚硬并包含果仁的部分：桃～。杏～。像核的东西
苹果核的“核”字应读：hé。在汉语中，“核”字是一个多音字，其主要的读音是“hé”，表示果实中坚硬的种子部分，比如苹果核、桃核等。这个读音在日常生活中非常常见，并且与果实的结构紧密相关。"""
        doc3 = """果实中坚硬并包含果仁
“苹果核”的“核”字，应读：hé “枣核”的“核”字，应读：hé “桃核”的“核”字，应读：hé 核的读音：hú，hé 汉字注音： ㄏㄨˊ，汉字部首：木 笔画顺序名称：横、竖、撇、点、点、横、撇折、撇、撇、点。释义：核（hé）果实中坚硬并包含果仁的部分：桃～。杏～。像核的东西
苹果核的“核”字应读：hé。在汉语中，“核”字是一个多音字，其主要的读音是“hé”，表示果实中坚硬的种子部分，比如苹果核、桃核等。这个读音在日常生活中非常常见，并且与果实的结构紧密相关。"""
        fp1 = calculate_fingerprint(doc1)
        fp2 = calculate_fingerprint(doc2)
        fp3 = calculate_fingerprint(doc3)
        print(f"fps: {fp1}, {fp2}, {fp3}")
        print(f"dist 1&2: {compare_fingerprint(fp1, fp2)}, dist 2&3: {compare_fingerprint(fp2, fp3)}")


if __name__ == '__main__':
    unittest.main()

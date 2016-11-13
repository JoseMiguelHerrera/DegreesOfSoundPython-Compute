class emailSegments:
    """contains all the HTML email segments needed to send the result email"""

    htmlTOP= """ 
<head>
  <style type="text/css">
  @import url(https://fonts.googleapis.com/css?family=Montserrat);
               
  a {
    text-decoration: none;
    border: 0;
    outline: none;
    color: #bbbbbb;
  }                 

  </style>

  <style type="text/css" media="screen">
      @media screen {
        td, h1, h2, h3 {
          font-family: 'Montserrat', 'Helvetica Neue', 'Arial', 'sans-serif' !important;
        }
      }
  </style>

  <style type="text/css" media="only screen and (max-width: 480px)">
    /* Mobile styles */
    @media only screen and (max-width: 480px) {

      table[class="w320"] {
        width: 320px !important;
      }


    }
  </style>        
</head>
<body style="font-size: 14px;width: 100%; height: 100%; color: #ecf0f1; background: #ecf0f1; font-size: 14px; padding:0; margin:0; display:block; -webkit-text-size-adjust:none; -webkit-font-smoothing:antialiased;" bgcolor="#ecf0f1">
    
<table align="center" cellpadding="0" cellspacing="0" width="100%" height="100%" >
  <tr>
    <td style="text-align: center" align="center" valign="top" bgcolor="#333333"  width="100%">  

      <center>
      <br>
        <table style="margin: 0 auto;" cellpadding="0" cellspacing="0" width="600" class="w320">
          <tr>
            <td style="text-align: center" align="center" valign="top">

                <table style="margin: 0 auto;" cellpadding="0" cellspacing="0" width="100%" style="margin:0 auto;">
                  <tr>
                    <td style="font-size: 30px; text-align:center;">
                      
                    
                      
                    </td>
                  </tr>
                </table>
				               <table style="margin: 0 auto;" cellpadding="0" cellspacing="0" width="100%" bgcolor="#333334">
                  <tr>
                    <td style="text-align: center">
                    <br>
                      <img src="http://degreesofsoundteamv2.mybluemix.net/images/logo2.png" width="200" height="200" alt="degrees of sound logo">
                        
                    </td>
                      
                  </tr>
                  <tr>
                      
                    <td style="color: white; font-size: 26px; font-family: Helvetica, Arial, sans-serif; text-align: center">
                        <br>
                      $topTitle
                    </td>
                  </tr>
                  <tr>
                    <td>

                      <center>
                        <table style="margin: 0 auto;" cellpadding="0" cellspacing="0" width="60%">
                          <tr>
                            <td style="color:#fff; font-family: Helvetica, Arial, sans-serif; text-align: center">
                            
Use this info to supercharge your career, and meet the right people!
                            <br>
                            <br>    
                            
                            </td>
                          </tr>
                        </table>
                      </center>

                    </td>
                  </tr>
                  
                </table>
"""




    htmlPathSectionTop="""
<table style="margin: 0 auto;" cellpadding="0" cellspacing="0" width="100%" bgcolor="$colorCode">
	<tr>
		<td style="background-color:$colorCode; color: white; font-size: 26px; font-family: Helvetica, Arial, sans-serif; text-align: center">
        	<br>
            The shortest path to $user, who has $followers_count followers, is:
        </td>
    </tr>                    
    <tr>
    	<td style="text-align: center">
"""



    htmlPathSectionTopNoPath="""
<table style="margin: 0 auto;" cellpadding="0" cellspacing="0" width="100%" bgcolor="$colorCode">
	<tr>
		<td style="background-color:$colorCode; color: white; font-size: 26px; font-family: Helvetica, Arial, sans-serif; text-align: center">
        </td>
    </tr>                    
    <tr>
    	<td style="text-align: center">
"""



    htmlInsertAvatar="""
<br>
	<a href="$permaLinkUrl"><img src="$picURL" width="100" height="100" style="border-radius:100%"/></a>                        
"""

    htmlInsertArrow="""
<br>                        
	<img src="http://degreesofsoundteamv2.mybluemix.net/images/arrow.png" width="20" height="52" />
"""


    htmlPathSectionBottomButton="""	
</td>
	</tr>
        <tr>                    
            </tr>
            	<tr>
                	<td style="text-align: center">
                    	<br>
                      	<div>
                        	<a class="try" href="http://degreesofsound.com" style="background-color: #b86114; border-radius: 4px; color: white; display: inline-block; font-family: Helvetica, Arial, sans-serif; font-size:16px; font-weight:bold; line-height:50px; text-align:center; text-decoration:none;text-decoration:none; width:200px;"
                      		>Try it again</a>
                        
                        </div>
                      	<br>
                     	 <br>
                    </td>
                </tr>
</table>

"""


    htmlPathSectionBottomNoButton="""
</td>
	</tr>
        <tr>                    
            </tr>
            	<tr>
                	<td style="text-align: center">
                     	 <br>
                    </td>
                </tr>
</table>

"""


    htmlBottom= """                                            
                <table style="margin: 0 auto;" cellpadding="0" cellspacing="0" width="100%" bgcolor="#333333" style="margin: 0 auto">
                  <tr>
                    <td style="background-color:#333333; text-align: center">
                      <br>
                    </td>
                  </tr>
                  <tr>
                    <td style="font-family: Helvetica, Arial, sans-serif; color:#bbbbbb; font-size:13px; text-align: center">
                    	<a style="color:#bbbbbb;" href="mailto:degreesofsoundbot@gmail.com?Subject=feedback" >Contact</a>
                      <br><br>
                    </td>
                  </tr>
				  <tr>
                    <td style="font-family: Helvetica, Arial, sans-serif; color:#bbbbbb; font-size:13px; text-align: center">
                    	<a style="color:#bbbbbb;" href="https://www.facebook.com/degreesofsoundsoftware/" >Like us on Facebook!</a>
                      <br><br>
                    </td>
                  </tr>
                  <tr>
                    <td style="font-family: Helvetica, Arial, sans-serif; color:#bbbbbb; font-size:13px; text-align: center">
                        Donate: <a href="bitcoin:1FWNaM53vP2rivVgNDp7rcXXNEubGATGzw?amount=0.0065&label=Degrees%20Of%20Sound%20Development">1FWNaM53vP2rivVgNDp7rcXXNEubGATGzw</a><br><br>
                       Degrees of Sound &copy; 2016
                       <br>
                       <br>
                    </td>
                      
                  </tr>
                </table>
				<br>




            </td>
          </tr>
        </table>
    </center>
    </td>
  </tr>
</table>
</body>
</html>

                

	"""
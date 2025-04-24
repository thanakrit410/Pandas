function doPost(e) {
  try {
    var json = JSON.parse(e.postData.contents);

    var message = json.text || 'No message';
    var sender = json.sender || 'Unknown';

    // เวลาเป็น Asia/Bangkok และรูปแบบ dd/MM/yyyy
    var timestamp = Utilities.formatDate(new Date(), "Asia/Bangkok", "dd/MM/yyyy HH:mm");

    writeToGoogleSheets(message, sender, timestamp);
    return ContentService.createTextOutput("Success");
  } catch (err) {
    return ContentService.createTextOutput("Error: " + err.message);
  }
}


function createNewSheetIfNotExists(dateObj) {

  if (!dateObj) {
    dateObj = new Date();
  }

  var sheetName = Utilities.formatDate(dateObj, "Asia/Bangkok", "d/M/yyyy");
  var ss = SpreadsheetApp.openById('1X24vrd4FNFOwlFLAoWsP8jlVd-uaRLfr_F6Jpd7XLiw');

  if (!ss.getSheetByName(sheetName)) {
    var newSheet = ss.insertSheet(sheetName);
    newSheet.appendRow(["Message", "Sender", "Timestamp"]); 
  }
}


function writeToGoogleSheets(message, sender, timestamp) {
  var dateObj = new Date();
  var sheetName = Utilities.formatDate(dateObj, "Asia/Bangkok", "d/M/yyyy");

  var ss = SpreadsheetApp.openById('1X24vrd4FNFOwlFLAoWsP8jlVd-uaRLfr_F6Jpd7XLiw');
  var sheet = ss.getSheetByName(sheetName);


  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
    sheet.appendRow(["Message", "Sender", "Timestamp"]);
  }


  sheet.appendRow([message, sender, timestamp]); 
}




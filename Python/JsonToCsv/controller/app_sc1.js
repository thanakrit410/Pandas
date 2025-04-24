function doGet(e) {
  try {
    var result = countAlarmWithWarningAndCriticalSummary();
    return ContentService.createTextOutput(JSON.stringify(result)).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput("Error: " + err.message);
  }
}

function doPost(e) {
  try {
    var result = countAlarmWithWarningAndCriticalSummary();
    return ContentService.createTextOutput(JSON.stringify(result)).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput("Error: " + err.message);
  }
}

function countAlarmWithWarningAndCriticalSummary() {
  var dateObj = new Date();
  
  dateObj.setDate(dateObj.getDate() - 1);
  var sheetName = Utilities.formatDate(dateObj, "Asia/Bangkok", "d/M/yyyy");

  var ss = SpreadsheetApp.openById('1X24vrd4FNFOwlFLAoWsP8jlVd-uaRLfr_F6Jpd7XLiw');
  var sheet = ss.getSheetByName(sheetName);

  if (!sheet) return { error: "No sheet found for " + sheetName };

  var data = sheet.getDataRange().getValues();
  var alarmCount = 0;
  var alarmWithWarning = {};
  var alarmWithCritical = {};
  var totalAlarmWithWarning = 0;
  var totalAlarmWithCritical = 0;

  for (var i = 1; i < data.length; i++) {
    var message = data[i][0];
    if (typeof message === "string" && message.includes("State: ALARM")) {
      alarmCount++;

      var appNameMatch = message.match(/App Name: ([\w\-]+)/);
      if (appNameMatch) {
        var appName = appNameMatch[1];

        if (message.includes("WARNING")) {
          alarmWithWarning[appName] = (alarmWithWarning[appName] || 0) + 1;
          totalAlarmWithWarning++;
        }

        if (message.includes("CRITICAL")) {
          alarmWithCritical[appName] = (alarmWithCritical[appName] || 0) + 1;
          totalAlarmWithCritical++;
        }
      }
    }
  }

  return {
    alarm: alarmCount,
    alarmWithWarning,
    alarmWithCritical,
    totalAlarmWithWarning,
    totalAlarmWithCritical
  };
}



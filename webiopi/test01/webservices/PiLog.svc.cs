using System;
using System.Linq;
using System.ServiceModel;
using System.ServiceModel.Channels;
using System.Net.Mail;
using System.Text;

namespace PiLogger
{
    public class PiLog : IPiLog
    {
        public string UploadLog(string Source,
                                string Level,
                                decimal Temperature)
        {

            //Resolve source IP
            RemoteEndpointMessageProperty messageProperty =
                OperationContext.Current.IncomingMessageProperties
                [RemoteEndpointMessageProperty.Name]
                as RemoteEndpointMessageProperty;
            string sIP = messageProperty.Address;

            //Create database context
            PiDataContext db = new PiDataContext();

            //Create new log entry
            TempLog log = new TempLog();
            log.Date_and_Time = DateTime.Now;
            log.Level = Level;
            log.Source = Source;
            log.IP = sIP;
            log.Temperature = Temperature;
            db.TempLogs.InsertOnSubmit(log);
            try
            {
                //Insert log in database
                db.SubmitChanges();
                return "OK";
            }
            catch (Exception ex)
            {
                return "ERROR: " + ex.Message;
            }
            

        }

        public string Notify(string Name,
                             decimal Temperature)
        {
            //Create database context
            PiDataContext db = new PiDataContext();

            string sFrom = "noreply@rototron.info";
            string sTo = string.Empty;
            try
            {
                //Look up email address of recipient
                var Names = from n in db.Emails
                            where n.DisplayName == Name
                            select n.EmailAddress;

                //Confirm database match for recipient
                if (Names.Count() == 0)
                {
                    return "ERROR: Unable to find recipient "
                        + Name + " in database.";
                }
                else
                {
                    sTo = Names.First().ToString();
                }
            }
            catch (Exception ex)
            {
                return "ERROR: " + ex.Message;
            }
            try
            {
                using (MailMessage message = new MailMessage())
                {
                    //Build message
                    message.From = new MailAddress(sFrom);
                    message.To.Add(new MailAddress(sTo));
                    message.Subject = "Server Room Temperature Critical";
                    message.Body = string.Format("Server room at {0:F1}°F.",
                        Temperature);
                    message.IsBodyHtml = false;
                    //Specify your IIS SMTP server
                    SmtpClient smtp = new SmtpClient("10.0.0.70", 25);
                    smtp.Send(message);
                    return "OK";
                }
            }
            catch (Exception ex)
            {
                return "ERROR: " + ex.Message;
            }
        }


        public string GetLog(int Take)
        {
            //Create database context
            PiDataContext db = new PiDataContext();

            //Get log entries
            var logs = (from l in db.TempLogs
                       orderby l.Date_and_Time descending
                        select l).Take(Take).AsEnumerable().Reverse(); 
            //Check for no records
            int count = logs.Count();
            if (count == 0)
            {
                return null;
            }
            //Parse logs to string array
            StringBuilder sbLogs = new StringBuilder();
            foreach (TempLog log in logs)
            {
                if (sbLogs.Length > 0)
                {
                    sbLogs.Append(",");
                }
                sbLogs.Append(log.Date_and_Time.ToString());
                sbLogs.Append(",");
                sbLogs.Append(log.Temperature.ToString());
                
            }

            return sbLogs.ToString();
        }


    }
}

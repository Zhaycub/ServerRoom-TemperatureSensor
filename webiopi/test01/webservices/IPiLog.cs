using System.ServiceModel;

namespace PiLogger
{

    [ServiceContract]
    public interface IPiLog
    {
        [OperationContract]
        string UploadLog(string Source,
                         string Level,
                         decimal Temperature);

        [OperationContract]
        string Notify(string Name,
                      decimal Temperature);

        [OperationContract]
        string GetLog(int Take);
    }
}

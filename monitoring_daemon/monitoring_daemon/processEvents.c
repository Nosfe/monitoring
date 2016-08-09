#include <Python.h>

#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/connector.h>
#include <linux/cn_proc.h>
#include <signal.h>
#include <errno.h>
#include <stdbool.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

/*
* connect to netlink
* returns netlink socket, or -1 on error
*/
int nl_connect(void)
{
    int rc;
    int nl_sock;
    struct sockaddr_nl sa_nl;

    nl_sock = socket(PF_NETLINK, SOCK_DGRAM, NETLINK_CONNECTOR);
    if (nl_sock == -1) {
        perror("#[C] socket");
        return -1;
    }

    sa_nl.nl_family = AF_NETLINK;
    sa_nl.nl_groups = CN_IDX_PROC;
    sa_nl.nl_pid = getpid();

    rc = bind(nl_sock, (struct sockaddr *)&sa_nl, sizeof(sa_nl));
    if (rc == -1) {
        perror("#[C] bind");
        close(nl_sock);
        return -1;
    }

//    printf("#[C] Socket number is: %d\n", nl_sock);

    return nl_sock;
}

static PyObject *nl_connect_wrapper(PyObject *self){
    return Py_BuildValue("i", nl_connect());
}

int nl_close(int nl_sock)
{
    close(nl_sock);
    return 0;
}

static PyObject *nl_close_wrapper(PyObject *self, PyObject *args){
    int nl_sock;
    if(!PyArg_ParseTuple(args, "i", &nl_sock))
        return NULL;
    return Py_BuildValue("i", nl_close(nl_sock));
}


/*
* subscribe on proc events (process notifications)
*/
int set_proc_ev_listen(int nl_sock, bool enable)
{
    int rc;
    struct __attribute__ ((aligned(NLMSG_ALIGNTO))) {
        struct nlmsghdr nl_hdr;
        struct __attribute__ ((__packed__)) {
        struct cn_msg cn_msg;
        enum proc_cn_mcast_op cn_mcast;
        };
    } nlcn_msg;

    memset(&nlcn_msg, 0, sizeof(nlcn_msg));
    nlcn_msg.nl_hdr.nlmsg_len = sizeof(nlcn_msg);
    nlcn_msg.nl_hdr.nlmsg_pid = getpid();
    nlcn_msg.nl_hdr.nlmsg_type = NLMSG_DONE;

    nlcn_msg.cn_msg.id.idx = CN_IDX_PROC;
    nlcn_msg.cn_msg.id.val = CN_VAL_PROC;
    nlcn_msg.cn_msg.len = sizeof(enum proc_cn_mcast_op);

    nlcn_msg.cn_mcast = enable ? PROC_CN_MCAST_LISTEN : PROC_CN_MCAST_IGNORE;

//    printf("#[C] Sending message on socket number: %d\n", nl_sock);
//    printf("#[C] enable variable is set at: %d\n", enable);
    rc = send(nl_sock, &nlcn_msg, sizeof(nlcn_msg), 0);
    if (rc == -1) {
        perror("#[C] netlink send");
        return -1;
    }

    return 0;
}

static PyObject *set_proc_ev_listen_wrapper(PyObject *self, PyObject *args){
    int nl_sock;
    bool enable = true;
    if(!PyArg_ParseTuple(args, "i", &nl_sock))
        return NULL;
    return Py_BuildValue("i", set_proc_ev_listen(nl_sock, enable));
}

static PyObject *unset_proc_ev_listen_wrapper(PyObject *self, PyObject *args){
    int nl_sock;
    bool enable = false;
    if(!PyArg_ParseTuple(args, "i", &nl_sock))
        return NULL;

    return Py_BuildValue("i", set_proc_ev_listen(nl_sock, enable));
}

/*
 * handle a single process event
 * http://stackoverflow.com/questions/9305992/linux-threads-and-process
 */
int handle_proc_ev(int nl_sock, int parent_pid)
{
    int rc;
    struct __attribute__ ((aligned(NLMSG_ALIGNTO))) {
        struct nlmsghdr nl_hdr;
        struct __attribute__ ((__packed__)) {
            struct cn_msg cn_msg;
            struct proc_event proc_ev;
        };
    } nlcn_msg;

    Py_BEGIN_ALLOW_THREADS
    rc = recv(nl_sock, &nlcn_msg, sizeof(nlcn_msg), 0);
    Py_END_ALLOW_THREADS

    if (rc == 0) {
        /* shutdown? */
        return 0;
    } else if (rc == -1) {
        if (errno != EINTR){
//            perror("netlink recv");
            return -1;
        }
    }
    switch (nlcn_msg.proc_ev.what) {
        case PROC_EVENT_NONE:
//            printf("#[C] set mcast listen ok\n");
            break;
        case PROC_EVENT_FORK:
//            printf("#[C] Fork Event PPID: %d, CPID: %d, PTGID: %d, CTGID: %d\n",
//                        nlcn_msg.proc_ev.event_data.fork.parent_pid,
//                        nlcn_msg.proc_ev.event_data.fork.child_pid,
//                        nlcn_msg.proc_ev.event_data.fork.parent_tgid,
//                        nlcn_msg.proc_ev.event_data.fork.child_tgid
//
//            );
            if(nlcn_msg.proc_ev.event_data.fork.parent_tgid == parent_pid)
                return nlcn_msg.proc_ev.event_data.fork.child_tgid;
        case PROC_EVENT_EXEC:
//            printf("#[C] Exec Event PID: %d, TGID: %d\n",
//                        nlcn_msg.proc_ev.event_data.exec.process_pid,
//                        nlcn_msg.proc_ev.event_data.exec.process_tgid
//            );
            break;
        case PROC_EVENT_EXIT:
//            printf("#[C] Exit Event PID: %d, TGID: %d\n",
//                        nlcn_msg.proc_ev.event_data.exit.process_pid,
//                        nlcn_msg.proc_ev.event_data.exit.process_tgid
//            );
            return 0 - nlcn_msg.proc_ev.event_data.exit.process_tgid;
        case PROC_EVENT_UID:
//            printf("#[C] uid change: tid=%d pid=%d from %d to %d\n",
//                nlcn_msg.proc_ev.event_data.id.process_pid,
//                nlcn_msg.proc_ev.event_data.id.process_tgid,
//                nlcn_msg.proc_ev.event_data.id.r.ruid,
//                nlcn_msg.proc_ev.event_data.id.e.euid);
            break;
        case PROC_EVENT_GID:
//            printf("#[C] gid change: tid=%d pid=%d from %d to %d\n",
//                nlcn_msg.proc_ev.event_data.id.process_pid,
//                nlcn_msg.proc_ev.event_data.id.process_tgid,
//                nlcn_msg.proc_ev.event_data.id.r.rgid,
//                nlcn_msg.proc_ev.event_data.id.e.egid);
            break;
        default:
//            printf("#[C] unhandled proc event\n");
            break;
    }

    return 0;
}

static PyObject *handle_proc_ev_wrapper(PyObject *self, PyObject *args){
    int nl_sock, parent_pid;
    if(!PyArg_ParseTuple(args, "ii", &nl_sock, &parent_pid))
        return NULL;
    return Py_BuildValue("i", handle_proc_ev(nl_sock, parent_pid));
}

static PyMethodDef processEvents_methods[] = {
   { "handle_proc_ev", (PyCFunction)handle_proc_ev_wrapper, METH_VARARGS, NULL },
   { "nl_connect", (PyCFunction)nl_connect_wrapper, METH_NOARGS, NULL },
   { "set_proc_ev_listen", (PyCFunction)set_proc_ev_listen_wrapper, METH_VARARGS, NULL },
   { "unset_proc_ev_listen", (PyCFunction)unset_proc_ev_listen_wrapper, METH_VARARGS, NULL },
   { "nl_close", (PyCFunction)nl_close_wrapper, METH_VARARGS, NULL },
  { NULL, NULL, 0, NULL }
};


PyMODINIT_FUNC initprocessEvents(void) {
   (void) Py_InitModule3("processEvents", processEvents_methods, NULL);
}

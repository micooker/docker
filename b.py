# -*- coding:utf8 -*-

import os
import docker
import json
import psutil

class ContainerCollect(object):
    def __init__(self):
        self.client = docker.APIClient(base_url="unix://var/run/docker.sock")
        self.NumToLetter = {1: 'a', 2: 'b', 3:'c', 4:'d', 5:'e', 6:'f', 7:'g', 8:'h'}

    def GetNodeInfo(self):
        cpu_frequency = ""
        cpu_mode = self.client.info()["Architecture"]
        cpus = self.client.info()["NCPU"]
        disk_size = psutil.disk_usage("/var/lib/libvirt")[0]
        memory = self.client.info()["MemTotal"]
        try:
            sn = os.popen("dmidecode -t 1 |grep 'Serial Number'|awk -F': ' '{print $2}'")
            sn = sn.read().strip()
        except Exception as er:
            pass

        node_dict = {'cpu_mode': cpu_mode, 'memory': memory, 'disk': disk_size, 'cpu_frequency': cpu_frequency, 'sn': sn, 'cpus': cpus}
        return node_dict

    def GetContainerInfo(self):
        container_list = []
        containers = self.client.containers()
        for cs in containers:
            container_dict = {}
            uuid = cs["Id"]
            # cname = cs["Names"]
            i = self.client.inspect_container(uuid)
            s = self.client.stats(uuid,stream=False)

        ###################ID/NAME/TITLE Info##################
            name = i["Name"].strip("/")
            title = name

        ###################Mac Info############################
            for m in i["NetworkSettings"]["Networks"]:
                mac = i["NetworkSettings"]["Networks"][m]["MacAddress"]
        ###################Mem Info############################
            mem_used = s["memory_stats"]["usage"]
            mem_max = i["HostConfig"]["Memory"]
            cpu_time = s["cpu_stats"]["cpu_usage"]["total_usage"]
            cpu_max = i["HostConfig"]["NanoCpus"] / 1000000000
            cpu_max = int(cpu_max)
            mem_dict = {"cpu_time": cpu_time, "cpus": cpu_max, "max": mem_max, "used": mem_used}

        ###################Disk Info###########################
            disk_list = []
            vda_name = "vda"
            vda_max = psutil.disk_usage("/var/lib/libvirt/docker/containers/" + uuid)[0]
            vda_used = psutil.disk_usage("/var/lib/libvirt/docker/containers/" + uuid)[1]
            vda_physical = 0
            vda_dict = {"max": vda_max, "name": vda_name, "physical": vda_physical, "used": vda_used}
            disk_list.append(vda_dict)

            count = 2
            for j in i["Mounts"]:
                fs_label = j["Source"]
                fs_type = j["Type"]
                if fs_type == "bind":
                    disk_name = 'vd' + self.NumToLetter[count]
                    count = count + 1
                    disk_max = psutil.disk_usage(fs_label)[0]
                    disk_used = psutil.disk_usage(fs_label)[1]
                    disk_physical = 0
                    disk_dict = {"max": disk_max, "name": disk_name, "physical": disk_physical, "used": disk_used}
                    disk_list.append(disk_dict)
            container_dict = {"disks": disk_list, "mac": mac, "momory": mem_dict, "name": name, "title": title, "uuid": uuid}
            container_list.append(container_dict)
        return container_list

data_dict = {"node": ContainerCollect().GetNodeInfo(), "vms": ContainerCollect().GetContainerInfo()}
#ContainerCollect().GetContainerInfo()
print(json.dumps(data_dict))


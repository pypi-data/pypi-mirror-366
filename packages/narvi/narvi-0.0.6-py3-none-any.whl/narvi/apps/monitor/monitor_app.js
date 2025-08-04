/* MIT License

Narvi - a simple python web application server

Copyright (C) 2022-2024 Visual Topology Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

class MonitorApp {

    constructor(services, parameters) {
        this.services = services;
        this.services.add_message_listener(msg => this.recv(msg));
        this.status_table = document.getElementById("status_table");
    }


    recv(msg) {
        let o = JSON.parse(msg);
        this.status_table.innerHTML = "";
        function make_cell(txt, url) {
            let td = document.createElement("td");
            td.appendChild(document.createTextNode(""+txt));
            return td;
        }

        function make_app_link(app_name, app_url) {
            let a = document.createElement("a");
            a.setAttribute("href",app_url);
            a.setAttribute("class","app_link");
            a.setAttribute("target","_new");
            a.appendChild(document.createTextNode(app_name));
            return a;
        }

        function create_sparklines(metrics, h, lw, w, metrics_metadata, xstep) {
            let d = document.createElement("div");
            for(let metric in metrics) {
                let sd = document.createElement("div");
                let data = metrics[metric];
                let metadata = metrics_metadata[metric];
                let minmax_dp = metadata["minmax_decimal_places"] || 2;
                let display_minmax = metadata["minmax_display"];
                if (display_minmax === undefined) {
                    display_minmax = true;
                }

                var c = document.createElement("canvas");

                let ymin = metadata.min || 0;
                let ymax = metadata.max || 1;
                let colour = metadata.colour || "blue";
                c.setAttribute("width", w+lw);
                c.setAttribute("height", h);

                let ctx = c.getContext('2d');

                let height = c.height - 4;
                let width = c.width;
                ctx.clearRect(0, 0, width, height);
                let max_values = Math.floor(w / xstep);
                if (data.length > max_values) {
                    data.splice(0,data.length-max_values);
                    console.log(JSON.stringify(data));
                }
                let total = data.length;
                let vmax = Math.max.apply(Math, data);
                let vmin = Math.max.apply(Math, data);
                if (vmin < ymin) {
                    ymin = vmin;
                }
                if (vmax > ymax) {
                    ymax = vmax;
                }

                ctx.textAlign = "end";
                if (display_minmax) {
                    ctx.font = "normal 14px Courier";
                    ctx.textBaseline = "bottom";
                    ctx.strokeText(Number.parseFloat(ymin).toFixed(minmax_dp), lw - 5, h);
                    ctx.textBaseline = "top";
                    ctx.strokeText(Number.parseFloat(ymax).toFixed(minmax_dp), lw - 5, 0);
                }

                ctx.font = "normal 14px Courier";
                ctx.textBaseline = "middle";
                ctx.strokeText(metric, lw-5, h/2);

                let ystep = (ymax-ymin) / height;
                let x = lw+(w - total*xstep);
                let y = 2 + height - data[0] / ystep;
                let i = 0;

                ctx.beginPath();
                ctx.strokeStyle = colour;
                ctx.fillStyle = "green";
                let x0 = x;
                ctx.moveTo(x, 2+height);
                ctx.lineTo(x, y);
                for (i = 1; i < total; i = i + 1) {
                    x = x + xstep;
                    y = 2 + height - data[i] / ystep;
                    ctx.lineTo(x, y);
                }
                ctx.lineTo(x, 2+height);
                // ctx.To(x0, 2+height);
                ctx.stroke();
                ctx.fill();
                sd.appendChild(c);
                d.appendChild(sd);
            }
            return d;
        }

        function make_row(workspace, service_name, service_id, nr_sessions, uptime, apps, metrics, metrics_metadata) {
            let tr = document.createElement("tr");
            let app_url_div = document.createElement("div");
            for(let idx=0; idx<apps.length; idx++) {
                let app_name = apps[idx]["app_name"];
                let app_url = "../../../"+workspace+"/"+app_name+"/"+service_id+"/index.html";
                app_url_div.appendChild(make_app_link(app_name,app_url));
            }

            tr.appendChild(make_cell(workspace));
            tr.appendChild(make_cell(service_name));
            tr.appendChild(make_cell(service_id));
            tr.appendChild(app_url_div);
            tr.appendChild(make_cell(nr_sessions));
            tr.appendChild(make_cell(uptime));
            let colour = ""
            tr.appendChild(create_sparklines(metrics, 60, 100, 300, metrics_metadata,
                5));
            return tr;
        }

        for(let workspace in o) {
            for(let service_name in o[workspace]) {
                for(let service_id in o[workspace][service_name]["instances"]) {
                    for(let idx=0; idx<o[workspace][service_name]["instances"][service_id].length; idx++) {
                        let info = o[workspace][service_name]["instances"][service_id][idx];
                        let uptime = info.uptime || "?";
                        let nr_sessions = Object.keys(info.sessions || {}).length;
                        let apps = o[workspace][service_name]["apps"] || [];
                        let metrics = {};
                        if (info.metrics) {
                            for (let m = info.metrics.length-1; m >=0; m--) {
                                let mo = info.metrics[m][1];
                                for(let mk in mo) {
                                    if (!(mk in metrics)) {
                                        metrics[mk] = [];
                                    }
                                    metrics[mk].push(mo[mk]);
                                }
                            }
                        }
                        let tr = make_row(workspace, service_name, service_id, nr_sessions, uptime, apps, metrics, info.metrics_metadata || {});
                        this.status_table.appendChild(tr);
                    }
                }
            }
        }
    }
}
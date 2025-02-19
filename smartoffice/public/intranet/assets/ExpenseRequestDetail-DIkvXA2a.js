var qe=Object.defineProperty,Ae=Object.defineProperties;var Oe=Object.getOwnPropertyDescriptors;var ye=Object.getOwnPropertySymbols;var ze=Object.prototype.hasOwnProperty,Me=Object.prototype.propertyIsEnumerable;var fe=(n,d,i)=>d in n?qe(n,d,{enumerable:!0,configurable:!0,writable:!0,value:i}):n[d]=i,S=(n,d)=>{for(var i in d||(d={}))ze.call(d,i)&&fe(n,i,d[i]);if(ye)for(var i of ye(d))Me.call(d,i)&&fe(n,i,d[i]);return n},Q=(n,d)=>Ae(n,Oe(d));var re=(n,d,i)=>new Promise((f,m)=>{var s=$=>{try{w(i.next($))}catch(j){m(j)}},v=$=>{try{w(i.throw($))}catch(j){m(j)}},w=$=>$.done?f($.value):Promise.resolve($.value).then(s,v);w((i=i.apply(n,d)).next())});import{d as ae,P as ve,Q as ce,R as Ne,r as te,h as je,S as Be,w as ke,U as de,n as Ie,V as $e,v as L,o as g,c as h,x as Ce,C as l,b as ee,F as O,j as z,t as p,u as Le,L as He,q as ne,M as Ve,p as _e,y as Je,a as e,A as Ue,I as Ge,m as be,z as Z,e as le,J as We,_ as Ye}from"./index-Cyg4wGtG.js";import{U as Ke}from"./userLayout-BDzazd-1.js";import{U as Qe}from"./UserAvatar-cmCDRfxW.js";import{u as Xe}from"./useToast-Bg7Ixaa1.js";import{C as ie,B as Ze,p as et,a as tt,b as st,c as ot,d as rt,L as at}from"./chart-CHSKp0nA.js";import{_ as nt}from"./ApproversGrid.vue_vue_type_script_setup_true_lang-CHWhgJv5.js";import{u as J,w as lt}from"./xlsx-DaVhO591.js";const Ee={data:{type:Object,required:!0},options:{type:Object,default:()=>({})},plugins:{type:Array,default:()=>[]},datasetIdKey:{type:String,default:"label"},updateMode:{type:String,default:void 0}},ct={ariaLabel:{type:String},ariaDescribedby:{type:String}},dt=S(S({type:{type:String,required:!0},destroyDelay:{type:Number,default:0}},Ee),ct),it=Ne[0]==="2"?(n,d)=>Object.assign(n,{attrs:d}):(n,d)=>Object.assign(n,d);function X(n){return $e(n)?de(n):n}function pt(n){let d=arguments.length>1&&arguments[1]!==void 0?arguments[1]:n;return $e(d)?new Proxy(n,{}):n}function ut(n,d){const i=n.options;i&&d&&Object.assign(i,d)}function Te(n,d){n.labels=d}function Re(n,d,i){const f=[];n.datasets=d.map(m=>{const s=n.datasets.find(v=>v[i]===m[i]);return!s||!m.data||f.includes(s)?S({},m):(f.push(s),Object.assign(s,m),s)})}function xt(n,d){const i={labels:[],datasets:[]};return Te(i,n.labels),Re(i,n.datasets,d),i}const mt=ae({props:dt,setup(n,d){let{expose:i,slots:f}=d;const m=te(null),s=ve(null);i({chart:s});const v=()=>{if(!m.value)return;const{type:j,data:U,options:G,plugins:H,datasetIdKey:W}=n,Y=xt(U,W),P=pt(Y,U);s.value=new ie(m.value,{type:j,data:P,options:S({},G),plugins:H})},w=()=>{const j=de(s.value);j&&(n.destroyDelay>0?setTimeout(()=>{j.destroy(),s.value=null},n.destroyDelay):(j.destroy(),s.value=null))},$=j=>{j.update(n.updateMode)};return je(v),Be(w),ke([()=>n.options,()=>n.data],(j,U)=>{let[G,H]=j,[W,Y]=U;const P=de(s.value);if(!P)return;let K=!1;if(G){const R=X(G),F=X(W);R&&R!==F&&(ut(P,R),K=!0)}if(H){const R=X(H.labels),F=X(Y.labels),C=X(H.datasets),y=X(Y.datasets);R!==F&&(Te(P.config.data,R),K=!0),C&&C!==y&&(Re(P.config.data,C,n.datasetIdKey),K=!0)}K&&Ie(()=>{$(P)})},{deep:!0}),()=>ce("canvas",{role:"img",ariaLabel:n.ariaLabel,ariaDescribedby:n.ariaDescribedby,ref:m},[ce("p",{},[f.default?f.default():""])])}});function gt(n,d){return ie.register(d),ae({props:Ee,setup(i,f){let{expose:m}=f;const s=ve(null),v=w=>{s.value=w==null?void 0:w.chart};return m({chart:s}),()=>ce(mt,it({ref:v},S({type:n},i)))}})}const ht=gt("bar",Ze),yt={class:"relative"},we={__name:"ExpenseChart",props:{data:{type:Object,required:!0},type:{type:String,required:!0}},setup(n){ie.register(et,tt,st,ot,rt,at);const d=n,i=L(()=>{const m=Object.keys(d.data),s=Object.values(d.data).map(v=>v.reduce((w,$)=>w+(JSON.parse($.object_data).total_cost||0),0));return{labels:m,datasets:[{label:`${d.type} Distribution`,data:s,backgroundColor:["rgba(54, 162, 235, 0.5)","rgba(75, 192, 192, 0.5)","rgba(153, 102, 255, 0.5)","rgba(255, 159, 64, 0.5)","rgba(255, 99, 132, 0.5)"],borderColor:["rgba(54, 162, 235, 1)","rgba(75, 192, 192, 1)","rgba(153, 102, 255, 1)","rgba(255, 159, 64, 1)","rgba(255, 99, 132, 1)"],borderWidth:1}]}}),f={responsive:!0,maintainAspectRatio:!1,plugins:{legend:{display:!1}},scales:{y:{beginAtZero:!0,ticks:{callback:function(m){return"THB "+m.toLocaleString()}}}}};return(m,s)=>(g(),h("div",yt,[i.value?(g(),Ce(l(ht),{key:0,data:i.value,options:f},null,8,["data"])):ee("",!0)]))}},ft=()=>{const n=te([]),d=te(!1),i=te(null);return{expenseTypes:n,loading:d,error:i,fetchExpenseTypes:()=>re(void 0,null,function*(){d.value=!0;try{const s=yield(yield fetch("/api/method/frappe.client.get_list",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({doctype:"SMO Expense Type",fields:["name","description","for_expense","account_code"],filters:[["for_expense","=",1]],order_by:"description asc"})})).json();n.value=s.message||[]}catch(m){i.value=m,console.error("Error fetching expense types:",m)}finally{d.value=!1}})}},_t={class:"flex gap-2"},bt=["onClick"],wt=ae({__name:"ExpenseEntryChips",props:{entries:{}},setup(n){const d=i=>{window.open(`/app/smo-expense-entry/${i}`,"_blank")};return(i,f)=>(g(),h("div",_t,[(g(!0),h(O,null,z(i.entries,m=>(g(),h("button",{key:m,onClick:s=>d(m),class:"px-2 py-1 text-sm bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 hover:underline transition-colors"},p(m),9,bt))),128))]))}}),vt={class:"mx-auto px-4 py-6"},jt={class:"modal"},kt={class:"modal-box"},$t={class:"bg-white rounded-lg shadow p-6 mb-6"},Ct={class:"flex justify-between items-center"},Et={class:"flex gap-4"},Tt=["onClick","disabled"],Rt={key:0,class:"space-y-6"},Dt={class:"bg-white rounded-lg shadow p-4 sm:p-6"},St={class:"flex flex-col sm:flex-row justify-between items-start gap-4"},Pt={class:"flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4"},Ft={class:"text-lg sm:text-xl font-semibold text-gray-900"},qt={class:"text-xs sm:text-sm font-medium"},At={class:"mt-4 grid grid-cols-2 sm:grid-cols-4 gap-4"},Ot={class:"font-medium"},zt={class:"font-medium"},Mt={class:"font-medium"},Nt={class:"mt-4 space-y-2"},Bt={class:"flex items-center gap-2"},It={class:"flex flex-col"},Lt={class:"text-xs sm:text-sm text-gray-600"},Ht={class:"text-xs sm:text-sm text-gray-600"},Vt={key:0,class:"mt-2 text-xs sm:text-sm text-red-600"},Jt={class:"bg-blue-50 p-3 rounded-lg self-start"},Ut={class:"text-lg sm:text-xl font-bold text-blue-600"},Gt={class:"grid grid-cols-1 md:grid-cols-2 gap-6"},Wt={class:"bg-white rounded-lg shadow overflow-hidden"},Yt={class:"h-64 px-6"},Kt={class:"overflow-x-auto"},Qt={class:"min-w-full divide-y divide-gray-200"},Xt={class:"bg-white divide-y divide-gray-200"},Zt={class:"px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"},es={class:"px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900"},ts={class:"px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500"},ss={class:"bg-gray-50"},os={class:"px-6 py-4 whitespace-nowrap text-sm text-right font-bold text-blue-600"},rs={class:"px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500"},as={class:"bg-white rounded-lg shadow overflow-hidden"},ns={class:"h-64 px-6"},ls={class:"overflow-x-auto"},cs={class:"min-w-full divide-y divide-gray-200"},ds={class:"bg-white divide-y divide-gray-200"},is={class:"px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"},ps={class:"px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900"},us={class:"px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500"},xs={class:"bg-gray-50"},ms={class:"px-6 py-4 whitespace-nowrap text-sm text-right font-bold text-blue-600"},gs={class:"px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500"},hs={class:"bg-white rounded-lg shadow"},ys={class:"overflow-x-auto"},fs={class:"min-w-full divide-y divide-gray-200"},_s={class:"bg-gray-50"},bs={class:"bg-white divide-y divide-gray-200"},ws={class:"px-3 py-4 text-sm text-gray-900 whitespace-nowrap"},vs={class:"px-3 py-4 text-sm text-gray-900 whitespace-nowrap"},js={class:"px-3 py-4 text-sm text-gray-900 whitespace-nowrap"},ks={class:"px-3 py-4 text-sm text-gray-900 whitespace-nowrap"},$s={class:"px-3 py-4 text-sm text-gray-900 whitespace-nowrap"},Cs={class:"px-3 py-4 text-sm text-gray-900 whitespace-nowrap"},Es={class:"px-3 py-4 text-sm text-right font-medium text-blue-600 whitespace-nowrap"},Ts={class:"bg-gray-50"},Rs={class:"px-3 py-4 text-sm text-right font-medium text-blue-600 whitespace-nowrap"},Ds={class:"bg-white rounded-lg shadow mt-6"},Ss={class:"overflow-x-auto"},Ps={class:"min-w-full divide-y divide-gray-200",id:"attachments-table"},Fs={class:"bg-white divide-y divide-gray-200"},qs={class:"px-6 py-4 whitespace-nowrap text-sm text-gray-900"},As={class:"px-6 py-4 whitespace-nowrap text-sm text-gray-900"},Os={class:"px-6 py-4 whitespace-nowrap text-sm text-gray-900"},zs={class:"px-6 py-4 whitespace-nowrap text-sm text-gray-900"},Ms={class:"px-6 py-4 whitespace-nowrap text-sm text-gray-900"},Ns={class:"px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900"},Bs={class:"px-6 py-4 whitespace-nowrap text-sm text-center no-print"},Is=["href"],Ls={class:"bg-gray-50"},Hs={class:"px-6 py-4 whitespace-nowrap text-sm font-medium text-right text-blue-600"},Vs={key:0,class:"text-center py-8"},Js=ae({__name:"ExpenseRequestDetail",setup(n){const d=Le(),i=He(),f=Xe(),m=ne({url:"frappe.model.workflow.get_transitions",auto:!1,transform:r=>{const t=r.reduce((a,o)=>{const u=`${o.state}-${o.action}-${o.next_state}`;return a[u]||(a[u]=o),a},{});return Object.values(t)}}),s=Ve({doctype:"SMO Expense Request",name:i.params.id,auto:!0}),v=ne({url:"frappe.model.workflow.apply_workflow",auto:!1,onSuccess:()=>{s.reload()}}),w=te(""),$=r=>re(this,null,function*(){var t;try{if(r.action==="Reject")try{const a=yield fetch("/api/method/smartoffice.api.expense.update_reject_reason",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({doctype:"SMO Expense Request",docname:i.params.id,reject_reason:w.value})}),o=yield a.json();if(!a.ok){const u=o._server_messages?JSON.parse(JSON.parse(o._server_messages)[0]).message:"ไม่สามารถบันทึกเหตุผลการ Reject ได้";f.error(u);return}}catch(a){f.error("เกิดข้อผิดพลาดในการบันทึกเหตุผลการ Reject");return}yield v.submit({doc:s.doc,action:r.action}),f.success("บันทึกข้อมูลสำเร็จ")}catch(a){let o="เกิดข้อผิดพลาดในการดำเนินการ";(t=v.error)!=null&&t.messages&&(o=v.error.messages.join(", ")),f.error(o)}});ne({url:"frappe.desk.form.save.cancel",auto:!1,onSuccess:()=>{s.reload(),f.success("เอกสารถูกยกเลิกเรียบร้อยแล้ว")},onError:r=>{var t;f.error(((t=r.messages)==null?void 0:t.join(", "))||"ไม่สามารถยกเลิกเอกสารได้")}});const j=r=>{r.action==="Reject"?document.getElementById("reject-modal").checked=!0:$(r)},U=()=>re(this,null,function*(){if(!w.value){alert("Please enter a reason for rejection");return}yield $({action:"Reject"})}),G=()=>{d.go(-1)},H=()=>{window.open(`/app/smo-expense-request/${i.params.id}?from_page=/intranet`,"_blank")};ke(()=>s.doc,r=>{r&&m.fetch({doc:r})},{immediate:!0});const W=L(()=>{var r;return(r=s.doc)!=null&&r.expense_request_item?s.doc.expense_request_item.reduce((t,a)=>{const o=JSON.parse(a.object_data||"{}"),u=o.project_name||"Uncategorized";return t[u]||(t[u]=[]),t[u].push(Q(S({},a),{parsedData:o})),t},{}):{}}),Y=r=>r.reduce((t,a)=>{const o=a.parsedData;return t+(o.total_cost||0)},0),P=L(()=>{var r;return(r=s.doc)!=null&&r.expense_request_item?s.doc.expense_request_item.reduce((t,a)=>{const o=JSON.parse(a.object_data||"{}"),u=o.expense_type_desc||"Uncategorized";return t[u]||(t[u]=[]),t[u].push(Q(S({},a),{parsedData:o})),t},{}):{}}),K=r=>r.reduce((t,a)=>{const o=a.parsedData;return t+(o.total_cost||0)},0),R=L(()=>{var t;if(!((t=s.doc)!=null&&t.expense_request_item))return[];const r=new Map;return s.doc.expense_request_item.forEach(a=>{const o=JSON.parse(a.object_data||"{}"),u=`${o.service_date}-${o.customer_name}-${o.project_name}-${o.receipt_date}`;r.has(u)||r.set(u,S({key:u,project:o.project,service_date:o.service_date,customer_name:o.customer_name,project_name:o.project_name,receipt_date:o.receipt_date,total:0,expenseEntries:new Set},Object.fromEntries(D.value.map(q=>[q.name,0]))));const E=r.get(u);E[o.expense_type]=(E[o.expense_type]||0)+o.total_cost,E.total+=o.total_cost,E.expenseEntries.add(a.expense)}),Array.from(r.values()).map(a=>Q(S({},a),{expenseEntries:Array.from(a.expenseEntries)})).sort((a,o)=>`${a.service_date}${a.customer_name}${a.project_name}${a.receipt_date}`.localeCompare(`${o.service_date}${o.customer_name}${o.project_name}${o.receipt_date}`))}),F=L(()=>R.value.length?R.value.reduce((r,t)=>(D.value.forEach(a=>{r[a.name]=(r[a.name]||0)+(t[a.name]||0)}),r.total=(r.total||0)+t.total,r),{}):{});L(()=>{var t;if(!((t=s.doc)!=null&&t.expense_request_item))return[];const r=new Map;return s.doc.expense_request_item.forEach(a=>{const o=JSON.parse(a.object_data||"{}");if(!o.attachment)return;const u=`${o.service_date}-${o.customer_name}-${o.project_name}`;r.has(u)||r.set(u,{service_date:o.service_date,customer_name:o.customer_name,project_name:o.project_name,attachments:[]}),r.get(u).attachments.push({file_url:o.attachment,expense_type:o.expense_type_desc,receipt_date:o.receipt_date,total_cost:o.total_cost})}),Array.from(r.values()).sort((a,o)=>`${a.service_date}${a.customer_name}${a.project_name}`.localeCompare(`${o.service_date}${o.customer_name}${o.project_name}`))});const C=_e("formatDate"),y=_e("formatCurrency"),{expenseTypes:D,loading:Us,fetchExpenseTypes:De}=ft();je(()=>{De()});const Se=()=>{var u,E,q,_,A,V,M,N,B,c,b;const r=window.open("","_blank");if(!r)return;const t=R.value.map(k=>`
    <tr>
      <td>${C(k.service_date)}</td>
      <td>${k.project||""}</td>
      <td>${k.customer_name}</td>
      <td>${k.project_name}</td>
      <td>${C(k.receipt_date)}</td>
      <td>${k.expenseEntries.join(", ")}</td>
      ${D.value.map(oe=>`
        <td class="text-right">${y(k[oe.name]||0)}</td>
      `).join("")}
      <td class="text-right">${y(k.total)}</td>
    </tr>
  `).join(""),a=D.value.map(k=>`<th class="text-right">${k.description}</th>`).join(""),o=D.value.map(k=>`<td class="text-right">${y(F.value[k.name]||0)}</td>`).join("");r.document.write(`
    <html>
      <head>
        <title>Expense Details - ${(u=s.doc)==null?void 0:u.name}</title>
        <style>
          @page {
            size: landscape;
            margin: 10mm;
          }
          body { 
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 15px;
            font-size: 12px;
          }
          .header {
            margin-bottom: 20px;
          }
          .header-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 15px;
          }
          .header-item {
            display: flex;
            gap: 10px;
          }
          .header-label {
            color: #666;
            min-width: 80px;
          }
          .header-value {
            font-weight: 500;
          }
          .doc-title {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 15px;
          }
          .total-amount {
            text-align: right;
            font-weight: bold;
            color: #1d4ed8;
            margin: 10px 0;
          }
          table { 
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1rem;
            font-size: 11px;
          }
          th, td { 
            border: 1px solid #000;
            padding: 6px;
            text-align: left;
          }
          th {
            background-color: #f8f9fa !important;
            -webkit-print-color-adjust: exact;
          }
          .text-right {
            text-align: right;
          }
          tfoot td {
            font-weight: bold;
          }
        </style>
      </head>
      <body>
        <div class="header">
          <div class="doc-title">
            Expense Request - ${(E=s.doc)==null?void 0:E.name}
          </div>
          <div class="header-grid">
            <div class="header-item">
              <span class="header-label">Year:</span>
              <span class="header-value">${(q=s.doc)==null?void 0:q.year}</span>
            </div>
            <div class="header-item">
              <span class="header-label">Month:</span>
              <span class="header-value">${(_=s.doc)==null?void 0:_.month}</span>
            </div>
            <div class="header-item">
              <span class="header-label">Period:</span>
              <span class="header-value">${(A=s.doc)==null?void 0:A.period}</span>
            </div>
            <div class="header-item">
              <span class="header-label">Request by:</span>
              <span class="header-value">${(V=s.doc)==null?void 0:V.request_by}</span>
            </div>
            <div class="header-item">
              <span class="header-label">Created on:</span>
              <span class="header-value">${(B=(N=(M=s.doc)==null?void 0:M.creation)==null?void 0:N.split(".")[0])==null?void 0:B.replace("T"," ")}</span>
            </div>
            <div class="header-item">
              <span class="header-label">Status:</span>
              <span class="header-value">${(c=s.doc)==null?void 0:c.workflow_state}</span>
            </div>
          </div>
          <div class="total-amount">
            Total Amount: ${y(((b=s.doc)==null?void 0:b.total)||0)}
          </div>
        </div>

        <table>
          <thead>
            <tr>
              <th>Service Date</th>
              <th>Project Code</th>
              <th>Customer</th>
              <th>Project</th>
              <th>Receipt Date</th>
              <th>Expense Entries</th>
              ${a}
              <th class="text-right">Total</th>
            </tr>
          </thead>
          <tbody>
            ${t}
          </tbody>
          <tfoot>
            <tr>
              <td colspan="6">Grand Total</td>
              ${o}
              <td class="text-right">${y(F.value.total||0)}</td>
            </tr>
          </tfoot>
        </table>
      </body>
    </html>
  `),r.document.close(),r.print()},Pe=()=>{var a,o;const r=window.open("","_blank");if(!r)return;const t=se.value.map(u=>`
    <tr>
      <td>${C(u.service_date)}</td>
      <td>${u.customer_name}</td>
      <td>${u.project_name}</td>
      <td>${u.expense_type_desc}</td>
      <td>${C(u.receipt_date)}</td>
      <td class="text-right">${y(u.total_cost)}</td>
    </tr>
  `).join("");r.document.write(`
    <html>
      <head>
        <title>Expense Attachments - ${(a=s.doc)==null?void 0:a.name}</title>
        <style>
          body { 
            font-family: Arial, sans-serif;
            margin: 20px;
            font-size: 12px;
          }
          h2 { 
            margin-bottom: 20px;
            font-size: 14px;
          }
          table { 
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1rem;
          }
          th, td { 
            border: 1px solid #000;
            padding: 8px;
            text-align: left;
          }
          th {
            background-color: #f8f9fa !important;
            -webkit-print-color-adjust: exact;
          }
          .text-right {
            text-align: right;
          }
          tfoot td {
            font-weight: bold;
          }
        </style>
      </head>
      <body>
        <h2>Expense Attachments - ${(o=s.doc)==null?void 0:o.name}</h2>
        <table>
          <thead>
            <tr>
              <th>Service Date</th>
              <th>Customer</th>
              <th>Project</th>
              <th>Expense Type</th>
              <th>Receipt Date</th>
              <th class="text-right">Amount</th>
            </tr>
          </thead>
          <tbody>
            ${t}
          </tbody>
          <tfoot>
            <tr>
              <td colspan="5">Total</td>
              <td class="text-right">${y(pe.value)}</td>
            </tr>
          </tfoot>
        </table>
      </body>
    </html>
  `),r.document.close(),r.print()},se=L(()=>{var r;return(r=s.doc)!=null&&r.expense_request_item?s.doc.expense_request_item.filter(t=>JSON.parse(t.object_data||"{}").attachment).map(t=>{const a=JSON.parse(t.object_data||"{}");return{service_date:a.service_date,customer_name:a.customer_name,project_name:a.project_name,expense_type_desc:a.expense_type_desc,receipt_date:a.receipt_date,total_cost:a.total_cost,file_url:a.attachment}}).sort((t,a)=>`${t.service_date}${t.customer_name}${t.project_name}`.localeCompare(`${a.service_date}${a.customer_name}${a.project_name}`)):[]}),pe=L(()=>se.value.reduce((r,t)=>r+(t.total_cost||0),0)),Fe=()=>{var M,N,B,c,b,k,oe,ue,xe,me,ge;const r={header:{font:{bold:!0,color:{rgb:"FFFFFF"}},fill:{patternType:"solid",fgColor:{rgb:"1F4E78"}},alignment:{horizontal:"left",vertical:"center"},border:{top:{style:"thin",color:{rgb:"000000"}},bottom:{style:"thin",color:{rgb:"000000"}},left:{style:"thin",color:{rgb:"000000"}},right:{style:"thin",color:{rgb:"000000"}}}},headerValue:{font:{bold:!0,size:11},fill:{patternType:"solid",fgColor:{rgb:"F2F2F2"}},alignment:{horizontal:"left",vertical:"center"},border:{top:{style:"thin",color:{rgb:"000000"}},bottom:{style:"thin",color:{rgb:"000000"}},left:{style:"thin",color:{rgb:"000000"}},right:{style:"thin",color:{rgb:"000000"}}}},tableHeader:{font:{bold:!0,color:{rgb:"FFFFFF"}},fill:{patternType:"solid",fgColor:{rgb:"366092"}},alignment:{horizontal:"center",vertical:"center",wrapText:!0},border:{top:{style:"thin",color:{rgb:"000000"}},bottom:{style:"thin",color:{rgb:"000000"}},left:{style:"thin",color:{rgb:"000000"}},right:{style:"thin",color:{rgb:"000000"}}}},cell:{alignment:{vertical:"center"},fill:{patternType:"solid",fgColor:{rgb:"FFFFFF"}},border:{top:{style:"thin",color:{rgb:"000000"}},bottom:{style:"thin",color:{rgb:"000000"}},left:{style:"thin",color:{rgb:"000000"}},right:{style:"thin",color:{rgb:"000000"}}}},numericCell:{alignment:{horizontal:"right",vertical:"center"},fill:{patternType:"solid",fgColor:{rgb:"FFFFFF"}},numFmt:"#,##0.00",border:{top:{style:"thin",color:{rgb:"000000"}},bottom:{style:"thin",color:{rgb:"000000"}},left:{style:"thin",color:{rgb:"000000"}},right:{style:"thin",color:{rgb:"000000"}}}},footer:{font:{bold:!0},fill:{patternType:"solid",fgColor:{rgb:"DCE6F1"}},alignment:{horizontal:"left",vertical:"center"},border:{top:{style:"thin",color:{rgb:"000000"}},bottom:{style:"double",color:{rgb:"000000"}},left:{style:"thin",color:{rgb:"000000"}},right:{style:"thin",color:{rgb:"000000"}}}},footerNumeric:{font:{bold:!0},fill:{patternType:"solid",fgColor:{rgb:"DCE6F1"}},alignment:{horizontal:"right",vertical:"center"},numFmt:"#,##0.00",border:{top:{style:"thin",color:{rgb:"000000"}},bottom:{style:"double",color:{rgb:"000000"}},left:{style:"thin",color:{rgb:"000000"}},right:{style:"thin",color:{rgb:"000000"}}}}},t=[["EXPENSE REQUEST DETAILS",(M=s.doc)==null?void 0:M.name],[""],["Year",(N=s.doc)==null?void 0:N.year],["Month",(B=s.doc)==null?void 0:B.month],["Period",(c=s.doc)==null?void 0:c.period],["Request by",(b=s.doc)==null?void 0:b.request_by],["Created on",(ue=(oe=(k=s.doc)==null?void 0:k.creation)==null?void 0:oe.split(".")[0])==null?void 0:ue.replace("T"," ")],["Status",(xe=s.doc)==null?void 0:xe.workflow_state],["Total Amount",y(((me=s.doc)==null?void 0:me.total)||0)],[""]],a=[["Service Date","Project Code","Customer","Project","Receipt Date",...D.value.map(x=>x.description),"Total"]],o=R.value.map(x=>[C(x.service_date),x.project||"",x.customer_name,x.project_name,C(x.receipt_date),...D.value.map(T=>x[T.name]||0),x.total]),u=[["Grand Total","","","","",...D.value.map(x=>F.value[x.name]||0),F.value.total||0]],E=[...t,...a,...o,...u],q=J.book_new(),_=J.aoa_to_sheet(E);_["!cols"]=[{wch:12},{wch:15},{wch:30},{wch:30},{wch:12},...D.value.map(()=>({wch:15})),{wch:15}],_["!rows"]=Array(E.length).fill({hpt:25});for(let x=0;x<t.length;x++)for(let T=0;T<2;T++){const I=J.encode_cell({r:x,c:T});_[I]&&(x===0?_[I].s=Q(S({},r.header),{font:Q(S({},r.header.font),{size:14})}):x>1&&(_[I].s=T===0?r.header:r.headerValue))}const A=t.length;for(let x=0;x<a[0].length;x++){const T=J.encode_cell({r:A,c:x});_[T]&&(_[T].s=r.tableHeader)}for(let x=0;x<o.length;x++){const T=A+1+x;for(let I=0;I<o[x].length;I++){const he=J.encode_cell({r:T,c:I});_[he]&&(_[he].s=I>=5?r.numericCell:r.cell)}}const V=A+1+o.length;for(let x=0;x<u[0].length;x++){const T=J.encode_cell({r:V,c:x});_[T]&&(_[T].s=x>=5?r.footerNumeric:r.footer)}_["!merges"]=[{s:{r:0,c:0},e:{r:0,c:a[0].length-1}}],J.book_append_sheet(q,_,"Expense Details"),lt(q,`expense-${(ge=s.doc)==null?void 0:ge.name}.xlsx`)};return(r,t)=>(g(),Ce(Ke,null,{default:Je(()=>{var a,o,u,E,q,_,A,V,M,N,B;return[e("div",vt,[t[35]||(t[35]=e("input",{type:"checkbox",id:"reject-modal",class:"modal-toggle"},null,-1)),e("div",jt,[e("div",kt,[t[2]||(t[2]=e("h3",{class:"font-bold text-lg"},"Please provide a reason for rejection",-1)),Ue(e("textarea",{"onUpdate:modelValue":t[0]||(t[0]=c=>w.value=c),class:"textarea textarea-bordered w-full mt-4",placeholder:"Reason..."},null,512),[[Ge,w.value]]),e("div",{class:"modal-action"},[e("label",{for:"reject-modal",class:"btn",onClick:U},"Confirm"),t[1]||(t[1]=e("label",{for:"reject-modal",class:"btn"},"Cancel",-1))])])]),e("div",$t,[e("div",Ct,[e("button",{onClick:G,class:"bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"}," Back "),e("div",Et,[(((a=l(s).doc)==null?void 0:a.workflow_state)==="Draft"||((o=l(s).doc)==null?void 0:o.workflow_state)==="Rejected")&&l(We).user===((u=l(s).doc)==null?void 0:u.owner)?(g(),h("button",{key:0,onClick:H,class:"bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded"}," Edit ")):ee("",!0),(g(!0),h(O,null,z(l(m).data,c=>(g(),h("button",{key:c.name,onClick:b=>j(c),disabled:l(v).loading,class:be({"bg-blue-500 hover:bg-blue-600":c.action==="Request Approve"||c.action==="Submit","bg-green-500 hover:bg-green-600":c.action==="Approve"||c.action==="Final Approve","bg-red-500 hover:bg-red-600":c.action==="Reject","opacity-50 cursor-not-allowed":l(v).loading,"text-white font-medium px-4 py-2 rounded-md transition-colors":!0})},p(c.action),11,Tt))),128))])])]),l(s).doc?(g(),h("div",Rt,[e("div",Dt,[e("div",St,[e("div",null,[e("div",Pt,[e("h1",Ft," Expense Request - "+p(l(s).doc.name),1),e("div",{class:be({"inline-flex border rounded-md px-2 py-1":!0,"bg-gray-100 border-gray-200 text-gray-700":l(s).doc.workflow_state==="Draft","bg-yellow-100 border-yellow-200 text-yellow-700":l(s).doc.workflow_state==="Approval Review"||l(s).doc.workflow_state==="Pending Approval","bg-green-100 border-green-200 text-green-700":l(s).doc.workflow_state==="Approved","bg-red-100 border-red-200 text-red-700":l(s).doc.workflow_state==="Rejected"})},[e("p",qt,p(l(s).doc.workflow_state),1)],2)]),e("div",At,[e("div",null,[t[3]||(t[3]=e("p",{class:"text-sm text-gray-500"},"Year",-1)),e("p",Ot,p(l(s).doc.year),1)]),e("div",null,[t[4]||(t[4]=e("p",{class:"text-sm text-gray-500"},"Month",-1)),e("p",zt,p(l(s).doc.month),1)]),e("div",null,[t[5]||(t[5]=e("p",{class:"text-sm text-gray-500"},"Period",-1)),e("p",Mt,p(l(s).doc.period),1)])]),e("div",Nt,[e("div",Bt,[Z(Qe,{email:l(s).doc.request_by,size:"sm"},null,8,["email"]),e("div",It,[e("p",Lt," Request by: "+p(l(s).doc.request_by),1),e("p",Ht," Created on: "+p((q=(E=l(s).doc.creation)==null?void 0:E.split(".")[0])==null?void 0:q.replace("T"," ")),1)])])]),l(s).doc.workflow_state==="Rejected"&&l(s).doc.reject_reason?(g(),h("p",Vt," Reject Reason: "+p(l(s).doc.reject_reason),1)):ee("",!0)]),e("div",Jt,[t[6]||(t[6]=e("p",{class:"text-xs sm:text-sm text-gray-600"},"Total Amount",-1)),e("p",Ut,p(l(y)(l(s).doc.total)),1)]),e("div",{class:"flex gap-2"},[e("button",{onClick:Se,class:"no-print inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"},t[7]||(t[7]=[e("svg",{class:"w-4 h-4 mr-2",fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},[e("path",{"stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",d:"M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"})],-1),le(" Print Details ")])),e("button",{onClick:Fe,class:"no-print inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"},t[8]||(t[8]=[e("svg",{class:"w-4 h-4 mr-2",fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},[e("path",{"stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",d:"M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"})],-1),le(" Export Excel ")]))])])]),e("div",Gt,[e("div",Wt,[t[11]||(t[11]=e("div",{class:"p-6 border-b border-gray-200"},[e("h2",{class:"text-lg font-medium text-gray-900"},"Summary by Expense Type")],-1)),e("div",Yt,[Z(we,{data:P.value,type:"Expense Type",chartType:"pie"},null,8,["data"])]),e("div",Kt,[e("table",Qt,[t[10]||(t[10]=e("thead",{class:"bg-gray-50"},[e("tr",null,[e("th",{scope:"col",class:"px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"}," Expense Type "),e("th",{scope:"col",class:"px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"}," Amount "),e("th",{scope:"col",class:"px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"}," Items ")])],-1)),e("tbody",Xt,[(g(!0),h(O,null,z(P.value,(c,b)=>(g(),h("tr",{key:b},[e("td",Zt,p(b),1),e("td",es,p(l(y)(K(c))),1),e("td",ts,p(c.length)+" items ",1)]))),128))]),e("tfoot",ss,[e("tr",null,[t[9]||(t[9]=e("td",{class:"px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"},"Grand Total",-1)),e("td",os,p(l(y)(((_=l(s).doc)==null?void 0:_.total)||0)),1),e("td",rs,p(((V=(A=l(s).doc)==null?void 0:A.expense_request_item)==null?void 0:V.length)||0)+" items ",1)])])])])]),e("div",as,[t[14]||(t[14]=e("div",{class:"p-6 border-b border-gray-200"},[e("h2",{class:"text-lg font-medium text-gray-900"},"Summary by Project")],-1)),e("div",ns,[Z(we,{data:W.value,type:"Project",chartType:"bar"},null,8,["data"])]),e("div",ls,[e("table",cs,[t[13]||(t[13]=e("thead",{class:"bg-gray-50"},[e("tr",null,[e("th",{scope:"col",class:"px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"}," Project "),e("th",{scope:"col",class:"px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"}," Amount "),e("th",{scope:"col",class:"px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"}," Items ")])],-1)),e("tbody",ds,[(g(!0),h(O,null,z(W.value,(c,b)=>(g(),h("tr",{key:b},[e("td",is,p(b),1),e("td",ps,p(l(y)(Y(c))),1),e("td",us,p(c.length)+" items ",1)]))),128))]),e("tfoot",xs,[e("tr",null,[t[12]||(t[12]=e("td",{class:"px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"},"Grand Total",-1)),e("td",ms,p(l(y)(((M=l(s).doc)==null?void 0:M.total)||0)),1),e("td",gs,p(((B=(N=l(s).doc)==null?void 0:N.expense_request_item)==null?void 0:B.length)||0)+" items ",1)])])])])])]),e("div",hs,[t[28]||(t[28]=e("div",{class:"p-6 border-b border-gray-200"},[e("h2",{class:"text-lg font-medium text-gray-900"},"Expense Items")],-1)),e("div",ys,[e("table",fs,[e("thead",_s,[e("tr",null,[t[15]||(t[15]=e("th",{scope:"col",class:"px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap"}," Service Date ",-1)),t[16]||(t[16]=e("th",{scope:"col",class:"px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap"}," Project Code ",-1)),t[17]||(t[17]=e("th",{scope:"col",class:"px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap"}," Customer ",-1)),t[18]||(t[18]=e("th",{scope:"col",class:"px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap"}," Project ",-1)),t[19]||(t[19]=e("th",{scope:"col",class:"px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap"}," Receipt Date ",-1)),t[20]||(t[20]=e("th",{scope:"col",class:"px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap"}," Expense Entries ",-1)),(g(!0),h(O,null,z(l(D),c=>(g(),h("th",{key:c.name,class:"px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase whitespace-nowrap"},p(c.description),1))),128)),t[21]||(t[21]=e("th",{scope:"col",class:"px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase whitespace-nowrap"}," Total ",-1))])]),e("tbody",bs,[(g(!0),h(O,null,z(R.value,c=>(g(),h("tr",{key:c.key},[e("td",ws,p(l(C)(c.service_date)),1),e("td",vs,p(c.project),1),e("td",js,p(c.customer_name),1),e("td",ks,p(c.project_name),1),e("td",$s,p(l(C)(c.receipt_date)),1),e("td",Cs,[Z(wt,{entries:c.expenseEntries},null,8,["entries"])]),(g(!0),h(O,null,z(l(D),b=>(g(),h("td",{key:b.name,class:"px-3 py-4 text-sm text-right text-gray-900 whitespace-nowrap"},p(l(y)(c[b.name])),1))),128)),e("td",Es,p(l(y)(c.total)),1)]))),128))]),e("tfoot",Ts,[e("tr",null,[t[22]||(t[22]=e("td",null," ",-1)),t[23]||(t[23]=e("td",null," ",-1)),t[24]||(t[24]=e("td",null," ",-1)),t[25]||(t[25]=e("td",null," ",-1)),t[26]||(t[26]=e("td",null," ",-1)),t[27]||(t[27]=e("td",{class:"px-3 py-4 text-sm font-medium text-gray-900 whitespace-nowrap sticky left-0 bg-gray-50"}," Grand Total ",-1)),(g(!0),h(O,null,z(l(D),c=>(g(),h("td",{key:c.name,class:"px-3 py-4 text-sm text-right font-medium text-gray-900 whitespace-nowrap"},p(l(y)(F.value[c.name])),1))),128)),e("td",Rs,p(l(y)(F.value.total)),1)])])])])]),e("div",Ds,[e("div",{class:"border-b border-gray-200"},[e("div",{class:"flex justify-between items-center px-6 py-4"},[t[30]||(t[30]=e("h2",{class:"text-lg font-medium text-gray-900"},"Attachments",-1)),e("button",{onClick:Pe,class:"no-print inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"},t[29]||(t[29]=[e("svg",{class:"w-4 h-4 mr-2",fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},[e("path",{"stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",d:"M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"})],-1),le(" Print ")]))])]),e("div",Ss,[e("table",Ps,[t[33]||(t[33]=e("thead",{class:"bg-gray-50"},[e("tr",null,[e("th",{scope:"col",class:"px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"}," Service Date "),e("th",{scope:"col",class:"px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"}," Customer "),e("th",{scope:"col",class:"px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"}," Project "),e("th",{scope:"col",class:"px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"}," Expense Type "),e("th",{scope:"col",class:"px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"}," Receipt Date "),e("th",{scope:"col",class:"px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"}," Amount "),e("th",{scope:"col",class:"px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider no-print"}," Attachment ")])],-1)),e("tbody",Fs,[(g(!0),h(O,null,z(se.value,(c,b)=>(g(),h("tr",{key:b},[e("td",qs,p(l(C)(c.service_date)),1),e("td",As,p(c.customer_name),1),e("td",Os,p(c.project_name),1),e("td",zs,p(c.expense_type_desc),1),e("td",Ms,p(l(C)(c.receipt_date)),1),e("td",Ns,p(l(y)(c.total_cost)),1),e("td",Bs,[e("a",{href:c.file_url,target:"_blank",class:"text-blue-600 hover:text-blue-900"}," View ",8,Is)])]))),128))]),e("tfoot",Ls,[e("tr",null,[t[31]||(t[31]=e("td",{colspan:"5",class:"px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"}," Total ",-1)),e("td",Hs,p(l(y)(pe.value)),1),t[32]||(t[32]=e("td",{class:"no-print"},null,-1))])])]),se.value.length===0?(g(),h("div",Vs,t[34]||(t[34]=[e("p",{class:"text-gray-500"},"ไม่พบเอกสารแนบ",-1)]))):ee("",!0)])]),Z(nt,{approvers:l(s).doc.approvers},null,8,["approvers"])])):ee("",!0)])]}),_:1}))}}),to=Ye(Js,[["__scopeId","data-v-09e05d69"]]);export{to as default};

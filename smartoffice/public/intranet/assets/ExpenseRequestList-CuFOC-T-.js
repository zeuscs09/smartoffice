var j=(O,C,s)=>new Promise((y,k)=>{var b=i=>{try{p(s.next(i))}catch(v){k(v)}},g=i=>{try{p(s.throw(i))}catch(v){k(v)}},p=i=>i.done?y(i.value):Promise.resolve(i.value).then(b,g);p((s=s.apply(O,C)).next())});import{d as H,u as Q,q as M,r as c,A as S,g as G,c as u,x as _,C as K,a as e,F as R,i as U,o as m,v as o,s as w,l as n,t as a,D as x,K as q,G as $,b as z,y as J,_ as W}from"./index-HzjLN9rv.js";import{U as X}from"./userLayout-CoZYfH6Y.js";import{u as Y}from"./expenseRequestStore-Bp5kfz5Z.js";import{U as D}from"./UserAvatar-DEtzeBnv.js";const Z={class:"container mx-auto p-4"},ee={class:"flex justify-between items-center mb-4"},te={class:"breadcrumbs text-sm"},se={class:"flex gap-2"},le={key:0,class:"flex flex-wrap gap-4 mb-4"},oe={class:"overflow-x-auto mt-4"},ae={class:"table table-zebra w-full"},ne={class:"ml-1"},re={class:"ml-1"},ie={class:"ml-1"},de={key:0},ue=["onClick"],me=["onClick"],ce={key:1},pe={key:1,class:"flex justify-between items-center mt-4"},ve={class:"join"},be=["disabled"],ge={class:"join-item btn"},fe=["disabled"],we={class:"text-sm text-gray-600 mt-2"},xe={class:"modal-box w-11/12 max-w-5xl"},ye={class:"timeline timeline-vertical"},ke={class:"text-sm"},_e={class:"timeline-middle"},Ce=H({__name:"ExpenseRequestList",setup(O){const C=Q(),s=Y(),y=M("formatDate"),k=M("formatCurrency"),b=c(""),g=c(""),p=c(""),i=c(""),v=c(10),f=c(!1),B=S(()=>s.data.length),E=S(()=>{var d;return((d=s.documentsResource.data)==null?void 0:d.total)||0});G(()=>{s.fetchAll(1)});const P=()=>{f.value=!f.value},L=()=>{s.searchQuery=b.value,s.fetchAll(1)},h=()=>{s.statusFilter=g.value,s.startDate=p.value,s.endDate=i.value,s.fetchAll(1)},F=d=>{s.sortField===d?s.sortOrder=s.sortOrder==="asc"?"desc":"asc":(s.sortField=d,s.sortOrder="asc"),s.fetchAll(1)},N=()=>{s.pageSize=v.value,s.fetchAll(1)},I=d=>{location.href=`/app/smo-service-report/${d}?from_page=service_report`},T=d=>j(this,null,function*(){var l;console.log(d);const t=J({doctype:"SMO Expense Request",name:d,auto:!1});yield t.reload(),console.log(t.doc.approvers),A.value=t.doc.approvers.map(r=>({date:r.action_date,status:r.status,action:r.status,approve_role:r.approver_role,by:r.user_id})),A.value.unshift({date:t.doc.creation,action:"Submit Request",status:"Approved",approve_role:"Requestor",by:t.doc.owner}),(l=V.value)==null||l.showModal()}),V=c(null),A=c([]);return(d,t)=>(m(),u(R,null,[_(X,null,{default:K(()=>[e("div",Z,[e("div",ee,[e("div",te,[e("ul",null,[e("li",null,[e("a",{onClick:t[0]||(t[0]=l=>o(C).push("/"))},"Home")]),t[11]||(t[11]=e("li",null,"Expense Request",-1))])]),e("div",se,[t[13]||(t[13]=e("button",{class:"btn btn-primary btn-sm"},[e("svg",{xmlns:"http://www.w3.org/2000/svg",class:"h-5 w-5",fill:"none",viewBox:"0 0 24 24",stroke:"currentColor"},[e("path",{"stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",d:"M12 4v16m8-8H4"})]),w(" เพิ่ม ")],-1)),e("button",{class:n(["btn btn-sm",{"btn-ghost":!f.value}]),onClick:P},[t[12]||(t[12]=e("svg",{xmlns:"http://www.w3.org/2000/svg",class:"h-5 w-5 mr-2",fill:"none",viewBox:"0 0 24 24",stroke:"currentColor"},[e("path",{"stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",d:"M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"})],-1)),w(" "+a(f.value?"ซ่อนตัวกรอง":"ตัวกรอง"),1)],2)])]),f.value?(m(),u("div",le,[x(e("input",{type:"text",placeholder:"No.,Task,Customer,Responsible",class:"input input-bordered input-sm flex-grow","onUpdate:modelValue":t[1]||(t[1]=l=>b.value=l),onInput:L},null,544),[[q,b.value]]),x(e("select",{class:"select select-bordered select-sm w-full max-w-xs","onUpdate:modelValue":t[2]||(t[2]=l=>g.value=l),onChange:h},t[14]||(t[14]=[e("option",{value:""},"ทุกสถานะ",-1),e("option",{value:"Open"},"เปิด",-1),e("option",{value:"Closed"},"ปิด",-1),e("option",{value:"Cancelled"},"ยกเลิก",-1)]),544),[[$,g.value]]),x(e("input",{type:"date",class:"input input-bordered input-sm","onUpdate:modelValue":t[3]||(t[3]=l=>p.value=l),onChange:h},null,544),[[q,p.value]]),x(e("input",{type:"date",class:"input input-bordered input-sm","onUpdate:modelValue":t[4]||(t[4]=l=>i.value=l),onChange:h},null,544),[[q,i.value]])])):z("",!0),e("div",oe,[e("table",ae,[e("thead",null,[e("tr",null,[e("th",{class:"cursor-pointer",onClick:t[5]||(t[5]=l=>F("name"))},[t[15]||(t[15]=w(" No. ")),e("span",ne,[e("span",{class:n({"text-primary":o(s).sortField==="name"})},a(o(s).sortField==="name"&&o(s).sortOrder==="asc"?"▲":"△"),3),e("span",{class:n({"text-primary":o(s).sortField==="name"})},a(o(s).sortField==="name"&&o(s).sortOrder==="desc"?"▼":"▽"),3)])]),e("th",{class:"cursor-pointer",onClick:t[6]||(t[6]=l=>F("workflow_state"))},[t[16]||(t[16]=w(" Amount ")),e("span",re,[e("span",{class:n({"text-primary":o(s).sortField==="workflow_state"})},a(o(s).sortField==="workflow_state"&&o(s).sortOrder==="asc"?"▲":"△"),3),e("span",{class:n({"text-primary":o(s).sortField==="workflow_state"})},a(o(s).sortField==="workflow_state"&&o(s).sortOrder==="desc"?"▼":"▽"),3)])]),e("th",{class:"cursor-pointer",onClick:t[7]||(t[7]=l=>F("creation"))},[t[17]||(t[17]=w(" Request Date ")),e("span",ie,[e("span",{class:n({"text-primary":o(s).sortField==="creation"})},a(o(s).sortField==="due_date"&&o(s).sortOrder==="asc"?"▲":"△"),3),e("span",{class:n({"text-primary":o(s).sortField==="creation"})},a(o(s).sortField==="creation"&&o(s).sortOrder==="desc"?"▼":"▽"),3)])]),t[18]||(t[18]=e("th",null,"Request By",-1)),t[19]||(t[19]=e("th",null,"Approver",-1))])]),o(s).data.length>0?(m(),u("tbody",de,[(m(!0),u(R,null,U(o(s).data,l=>(m(),u("tr",{key:l.name},[e("td",null,[e("div",{class:"cursor-pointer",onClick:r=>I(l.name)},a(l.name),9,ue),e("div",{class:n(["badge badge-sm",{"badge-primary":l.workflow_state==="Approved"}])},a(l.workflow_state),3)]),e("td",null,a(o(k)(l.total)),1),e("td",null,a(o(y)(l.creation)),1),e("td",null,[_(D,{email:l.request_by},null,8,["email"])]),e("td",null,[e("div",{class:"cursor-pointer",onClick:r=>T(l.name)},[_(D,{email:l.approvers},null,8,["email"])],8,me)])]))),128))])):(m(),u("tbody",ce,t[20]||(t[20]=[e("tr",null,[e("td",{colspan:"5",class:"text-center"},"ไม่พบข้อมูล")],-1)])))])]),o(s).data.length>0?(m(),u("div",pe,[e("div",ve,[e("button",{class:"join-item btn",onClick:t[8]||(t[8]=l=>o(s).previousPage()),disabled:o(s).isFirstPage}," « ",8,be),e("button",ge," หน้า "+a(o(s).currentPage),1),e("button",{class:"join-item btn",onClick:t[9]||(t[9]=l=>o(s).nextPage()),disabled:o(s).isLastPage}," » ",8,fe)]),x(e("select",{"onUpdate:modelValue":t[10]||(t[10]=l=>v.value=l),onChange:N,class:"select select-bordered"},t[21]||(t[21]=[e("option",{value:10},"10 รายการ/หน้า",-1),e("option",{value:20},"20 รายการ/หน้า",-1),e("option",{value:50},"50 รายการ/หน้า",-1)]),544),[[$,v.value]])])):z("",!0),e("div",we," แสดง "+a(B.value)+" จาก "+a(E.value)+" รายการ ",1)])]),_:1}),e("dialog",{id:"timeline_modal",class:"modal",ref_key:"timelineModal",ref:V},[e("div",xe,[t[23]||(t[23]=e("h3",{class:"font-bold text-lg mb-4"},"ประวัติการอนุมัติ",-1)),e("ul",ye,[(m(!0),u(R,null,U(A.value,(l,r)=>(m(),u("li",{key:r},[e("hr",{class:n({"bg-green-500":l.status==="Approved"})},null,2),e("div",{class:n([r%2===0?"timeline-start":"timeline-end","timeline-box"])},[e("div",{class:n(["flex items-center",{"flex-row-reverse":r%2===0}])},[_(D,{email:l.by,class:n([r%2===0?"ml-2":"mr-2"])},null,8,["email","class"]),e("div",null,[e("div",ke,a(l.approve_role),1),e("div",{class:n(["badge badge-sm",{"badge-success":l.status==="Approved","badge-danger":l.status==="Reject","badge-ghost":l.status==="Pending"}])},a(l.action),3)])],2)],2),e("div",_e,[(m(),u("svg",{xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 20 20",fill:"currentColor",class:n(["h-5 w-5",l.status==="Approved"?"text-green-500":"text-gray-500"])},t[22]||(t[22]=[e("path",{"fill-rule":"evenodd",d:"M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z","clip-rule":"evenodd"},null,-1)]),2))]),e("div",{class:n([r%2===0?"timeline-end":"timeline-start"])},a(l.date?o(y)(l.date):""),3),e("hr",{class:n({"bg-green-500":l.status==="Approved"})},null,2)]))),128))]),t[24]||(t[24]=e("div",{class:"modal-action"},[e("form",{method:"dialog"},[e("button",{class:"btn"},"ปิด")])],-1))])],512)],64))}}),De=W(Ce,[["__scopeId","data-v-efef0bbb"]]);export{De as default};
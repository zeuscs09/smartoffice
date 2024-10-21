import{d as z,u as A,m as V,r as l,q as x,g as P,w as B,v as w,x as _,o as g,a as s,B as o,l as D,c as O,z as u,H as f,C as L,b,y as U,_ as I}from"./index-BjUjyLbN.js";import{u as M}from"./userLayout-ZLl1ofLD.js";import{u as N,S as $}from"./ServiceReportTable-fI6O__nX.js";import{_ as j}from"./Pagination.vue_vue_type_script_setup_true_lang-BjD5Jrpi.js";import"./UserAvatar--QHl542-.js";import"./NoDataFoundTable-CQstSkm9.js";import"./NoDataFoundCard-Dr_8P_bw.js";const H={class:"container mx-auto p-4"},Q={class:"flex justify-between items-center mb-4"},T={class:"breadcrumbs text-sm"},q={key:0,class:"flex flex-wrap gap-4 mb-4"},E={class:"overflow-x-auto mt-4"},G=z({__name:"ServiceReportList",setup(J){const h=A(),e=N();e.pageSize=10,V("formatDate");const i=l(""),d=l(""),p=l(""),c=l(""),v=l(10),n=l(!1),C=x(()=>e.data.length),S=x(()=>{var a;return((a=e.documentsResource.data)==null?void 0:a.total)||0});P(()=>{e.fetchAll(1)});const y=()=>{n.value=!n.value},R=()=>{e.searchQuery=i.value,e.fetchAll(1)},m=()=>{e.statusFilter=d.value,e.startDate=p.value,e.endDate=c.value,e.fetchAll(1)},k=a=>{e.sortField===a?e.sortOrder=e.sortOrder==="asc"?"desc":"asc":(e.sortField=a,e.sortOrder="asc"),e.fetchAll(1)},F=a=>{v.value=a,e.pageSize=a,e.fetchAll(1)};return B(v,a=>{console.log("Page size changed to:",a)}),(a,t)=>(g(),w(M,null,{default:_(()=>[s("div",H,[s("div",Q,[s("div",T,[s("ul",null,[s("li",null,[s("a",{onClick:t[0]||(t[0]=r=>o(h).push("/"))},"Home")]),t[7]||(t[7]=s("li",null,"Service Report",-1))])]),s("button",{class:D(["btn btn-sm",{"btn-ghost":!n.value}]),onClick:y},t[8]||(t[8]=[s("svg",{xmlns:"http://www.w3.org/2000/svg",class:"h-5 w-5 mr-2",fill:"none",viewBox:"0 0 24 24",stroke:"currentColor"},[s("path",{"stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",d:"M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"})],-1)]),2)]),n.value?(g(),O("div",q,[u(s("input",{type:"text",placeholder:"Search...",class:"input input-bordered flex-grow","onUpdate:modelValue":t[1]||(t[1]=r=>i.value=r),onInput:R},null,544),[[f,i.value]]),u(s("select",{class:"select select-bordered w-full max-w-xs","onUpdate:modelValue":t[2]||(t[2]=r=>d.value=r),onChange:m},t[9]||(t[9]=[s("option",{value:""},"All Status",-1),s("option",{value:"Customer Review"},"Customer Review",-1),s("option",{value:"Customer Approve"},"Customer Approve",-1)]),544),[[L,d.value]]),u(s("input",{type:"date",class:"input input-bordered","onUpdate:modelValue":t[3]||(t[3]=r=>p.value=r),onChange:m},null,544),[[f,p.value]]),u(s("input",{type:"date",class:"input input-bordered","onUpdate:modelValue":t[4]||(t[4]=r=>c.value=r),onChange:m},null,544),[[f,c.value]])])):b("",!0),s("div",E,[U($,{data:o(e).data,loading:o(e).documentsResource.loading,error:o(e).documentsResource.error,sortField:o(e).sortField,sortOrder:o(e).sortOrder,sortable:!0,onSort:k},null,8,["data","loading","error","sortField","sortOrder"])]),o(e).data.length>0?(g(),w(j,{key:1,"current-page":o(e).currentPage,"is-first-page":o(e).isFirstPage,"is-last-page":o(e).isLastPage,"page-size":v.value,"displayed-items-count":C.value,"total-items":S.value,onPrevious:t[5]||(t[5]=r=>o(e).previousPage()),onNext:t[6]||(t[6]=r=>o(e).nextPage()),"onUpdate:pageSize":F},null,8,["current-page","is-first-page","is-last-page","page-size","displayed-items-count","total-items"])):b("",!0)])]),_:1}))}}),se=I(G,[["__scopeId","data-v-1eb0189a"]]);export{se as default};

import{U as c}from"./UserAvatar-X8AlCWQw.js";import{d as n,m,c as a,F as u,i as p,o as l,a as s,l as t,y as _,t as o,B as g}from"./index-by_FZnAW.js";const h={class:"timeline timeline-vertical"},f={class:"text-sm"},v={class:"timeline-middle"},b={key:0,"fill-rule":"evenodd",d:"M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z","clip-rule":"evenodd"},y={key:1,"fill-rule":"evenodd",d:"M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z","clip-rule":"evenodd"},w={key:2,"fill-rule":"evenodd",d:"M10 18a8 8 0 100-16 8 8 0 000 16zm0-2a6 6 0 100-12 6 6 0 000 12z","clip-rule":"evenodd"},A=n({__name:"TimeLine",props:{events:{}},setup(z){const d=m("formatDate");return(i,j)=>(l(),a("ul",h,[(l(!0),a(u,null,p(i.events,(e,r)=>(l(),a("li",{key:r},[s("hr",{class:t({"bg-green-500":e.status==="Approved","bg-red-500":e.status==="Rejected"})},null,2),s("div",{class:t([r%2===0?"timeline-start":"timeline-end","timeline-box"])},[s("div",{class:t(["flex items-center",{"flex-row-reverse":r%2===0}])},[_(c,{email:e.by,class:t([r%2===0?"ml-2":"mr-2"])},null,8,["email","class"]),s("div",null,[s("div",f,o(e.approve_role),1),s("div",{class:t(["badge badge-sm",{"badge-success":e.status==="Approved","badge-error":e.status==="Rejected","badge-ghost":e.status==="Pending"}])},o(e.action),3)])],2)],2),s("div",v,[(l(),a("svg",{xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 20 20",fill:"currentColor",class:t(["h-5 w-5",e.status==="Approved"?"text-green-500":e.status==="Rejected"?"text-red-500":"text-gray-500"])},[e.status==="Approved"?(l(),a("path",b)):e.status==="Rejected"?(l(),a("path",y)):(l(),a("path",w))],2))]),s("div",{class:t([r%2===0?"timeline-end":"timeline-start"])},o(e.date?g(d)(e.date):""),3),s("hr",{class:t({"bg-green-500":e.status==="Approved","bg-red-500":e.status==="Rejected"})},null,2)]))),128))]))}});export{A as _};
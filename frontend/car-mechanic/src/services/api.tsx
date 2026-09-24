import axios from "axios";

const  api=axios.create({
    baseURL:import.meta.env.VITE_API_BASE_URL,
    headers:{
        "Content-Type":"application/json",
    },
});

export const sendChatMessage=(data:any)=>
    api.post("/api/chat/",data);

export const uploadMedia=(FormData:any)=>
    api.post("/api/upload/",FormData,{
        headers:{
            "Content-Type":"multipart/form-data",
        },
    });

export const getDiagnosis=(data:any)=>
    api.post("/api/diagnosis/",data);

export const createBooking =(data:any)=>
    api.post("/api/booking/",data)

export const getBooking=(id:number)=>{
    api.get(`/api/booking/${id}/`);
}

export default api;
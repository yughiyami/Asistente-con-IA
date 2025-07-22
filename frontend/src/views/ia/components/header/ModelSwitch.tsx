import { Switch } from '@/components/ui/switch'
import React from 'react'
import api from '../../service/api';
import { useAppStore } from '@/store/store';

export default function ModelSwitch() {

    const { Modelmode, setModelMode } = useAppStore()
    const isPending = React.useRef(false);

    React.useEffect(() => {
        if (isPending.current) return;
        isPending.current = true;

        async function fetchModelStatus() {
            const status = await getModelStatus();
            setModelMode(status)
            isPending.current = false;
        }

        fetchModelStatus();
    }, []);

    function handleToggle() {
        if (isPending.current) return;
        isPending.current = true;

        async function updateModelStatus() {
            const newStatus = !Modelmode;
            const status = await setModelStatus(newStatus);
            if (!status) {
                console.error('Failed to update model status');
                isPending.current = false;
                return;
            }
            setModelMode(newStatus);
            isPending.current = false;
        }

        updateModelStatus();
    }

    return (
        <div className='flex items-center space-x-2'>
            <h2 className="text-md font-semibold">Extender modelo</h2>
            <Switch checked={!Modelmode} onCheckedChange={handleToggle} />
        </div>
    )
}

async function getModelStatus() {
    try {
        const response = await api.get('/chat/mode');
        return response.data === 'free' ? true : false;
    } catch (error) {
        console.error('Error fetching model status:', error);
        return false;
    }
        
}

async function setModelStatus(isFree: boolean) {
    try {
        const response = await api.post('/chat/mode', { mode: isFree ? 'free' : 'knowledge_base' });
        return response.status === 200;
    } catch (error) {
        console.error('Error setting model status:', error);
        throw error;
    }
}
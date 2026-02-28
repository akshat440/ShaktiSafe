import dynamic from 'next/dynamic';

const DashboardComponent = dynamic(() => import('./dashboard'), { ssr: false });

export default function Page() {
  return <DashboardComponent />;
}
